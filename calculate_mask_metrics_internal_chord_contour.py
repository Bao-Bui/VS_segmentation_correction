#!/usr/bin/env python3
"""
Calculate tumor volume and maximum CONTOUR-TO-CONTOUR INTERNAL CHORD diameters
for all NIfTI masks in a folder.

Definition
----------
For each axial, sagittal, and coronal 2D slice:

1. Convert the binary mask to its exact pixel-edge polygon.
2. Use OUTER contour vertices as candidate endpoints.
3. Test candidate endpoint pairs from longest to shortest.
4. Accept a candidate only if the ENTIRE straight line segment lies within
   the tumor polygon.
5. Keep the longest accepted segment as the slice's maximum internal chord.
6. Take the maximum across slices for each anatomical plane.
7. Take the maximum of axial, sagittal, and coronal.

No convex hull or alpha shape is used.

Dependencies
------------
    pip install nibabel numpy shapely

Usage
-----
    python calculate_mask_metrics_internal_chord_contour.py "C:\\path\\to\\post_processed"

Output
------
    post_processed_mask_metrics_internal_chord_contour.csv
"""

import argparse
import csv
import itertools
from pathlib import Path

import nibabel as nib
import numpy as np
from shapely.geometry import LineString, Polygon, MultiPolygon, box
from shapely.ops import unary_union


OUTPUT_CSV_NAME = "post_processed_mask_metrics_internal_chord_contour.csv"
GEOMETRY_TOL = 1e-9


def load_mask_canonical(path: Path):
    img = nib.load(str(path))
    img = nib.as_closest_canonical(img)
    data = np.squeeze(np.asanyarray(img.dataobj))
    if data.ndim != 3:
        raise ValueError(f"Expected a 3D mask, got shape {data.shape}")
    return data > 0, img.affine


def extract_slice(mask: np.ndarray, fixed_axis: int, slice_idx: int):
    if fixed_axis == 0:
        return mask[slice_idx, :, :]
    if fixed_axis == 1:
        return mask[:, slice_idx, :]
    return mask[:, :, slice_idx]


def inplane_vectors(affine: np.ndarray, fixed_axis: int):
    varying_axes = [ax for ax in range(3) if ax != fixed_axis]
    return affine[:3, varying_axes[0]], affine[:3, varying_axes[1]]


def contour_points_to_mm(points_rc: np.ndarray,
                         vec_row: np.ndarray,
                         vec_col: np.ndarray):
    return (
        points_rc[:, 0, None] * vec_row[None, :]
        + points_rc[:, 1, None] * vec_col[None, :]
    )


def foreground_runs(row: np.ndarray):
    cols = np.flatnonzero(row)
    if len(cols) == 0:
        return

    start = prev = int(cols[0])
    for c in cols[1:]:
        c = int(c)
        if c == prev + 1:
            prev = c
        else:
            yield start, prev
            start = prev = c
    yield start, prev


def build_exact_mask_polygon(slice_mask: np.ndarray):
    rectangles = []

    for r in range(slice_mask.shape[0]):
        for c0, c1 in foreground_runs(slice_mask[r]):
            rectangles.append(
                box(c0 - 0.5, r - 0.5, c1 + 0.5, r + 0.5)
            )

    if not rectangles:
        return None

    geom = unary_union(rectangles)

    if not geom.is_valid:
        geom = geom.buffer(0)

    return geom


def remove_consecutive_duplicates(points_xy: np.ndarray):
    if len(points_xy) <= 1:
        return points_xy

    keep = [0]
    for i in range(1, len(points_xy)):
        if not np.allclose(
            points_xy[i],
            points_xy[keep[-1]],
            rtol=0.0,
            atol=1e-12,
        ):
            keep.append(i)

    return points_xy[keep]


def remove_collinear_ring_vertices(points_xy: np.ndarray):
    pts = np.asarray(points_xy, dtype=float)

    if len(pts) >= 2 and np.allclose(
        pts[0], pts[-1], rtol=0.0, atol=1e-12
    ):
        pts = pts[:-1]

    pts = remove_consecutive_duplicates(pts)

    if len(pts) <= 2:
        return pts

    changed = True

    while changed and len(pts) > 2:
        changed = False
        keep = []
        n = len(pts)

        for i in range(n):
            p_prev = pts[(i - 1) % n]
            p = pts[i]
            p_next = pts[(i + 1) % n]

            v1 = p - p_prev
            v2 = p_next - p

            cross = v1[0] * v2[1] - v1[1] * v2[0]
            dot = float(np.dot(v1, v2))

            if abs(cross) <= 1e-12 and dot >= 0:
                changed = True
                continue

            keep.append(i)

        if keep:
            pts = pts[keep]
        else:
            break

    return pts


def outer_contour_vertices_rc(geom):
    if geom is None or geom.is_empty:
        return np.empty((0, 2), dtype=float)

    if isinstance(geom, Polygon):
        polygons = [geom]
    elif isinstance(geom, MultiPolygon):
        polygons = list(geom.geoms)
    elif hasattr(geom, "geoms"):
        polygons = [g for g in geom.geoms if isinstance(g, Polygon)]
    else:
        polygons = []

    all_rc = []

    for poly in polygons:
        xy = np.asarray(poly.exterior.coords, dtype=float)
        xy = remove_collinear_ring_vertices(xy)

        if len(xy) == 0:
            continue

        rc = np.column_stack([xy[:, 1], xy[:, 0]])
        all_rc.append(rc)

    if not all_rc:
        return np.empty((0, 2), dtype=float)

    pts = np.vstack(all_rc)
    pts = np.unique(np.round(pts, decimals=12), axis=0)
    return pts


def max_internal_chord_slice_mm(slice_mask: np.ndarray,
                                vec_row: np.ndarray,
                                vec_col: np.ndarray):
    geom = build_exact_mask_polygon(slice_mask)

    if geom is None or geom.is_empty:
        return 0.0

    points_rc = outer_contour_vertices_rc(geom)

    if len(points_rc) < 2:
        return 0.0

    points_mm = contour_points_to_mm(points_rc, vec_row, vec_col)

    candidates = []

    for i, j in itertools.combinations(range(len(points_rc)), 2):
        d_mm = float(np.linalg.norm(points_mm[i] - points_mm[j]))
        candidates.append((d_mm, i, j))

    candidates.sort(key=lambda x: x[0], reverse=True)

    containment_geom = geom.buffer(GEOMETRY_TOL)

    for d_mm, i, j in candidates:
        r1, c1 = points_rc[i]
        r2, c2 = points_rc[j]

        line = LineString([
            (float(c1), float(r1)),
            (float(c2), float(r2)),
        ])

        if containment_geom.covers(line):
            return d_mm

    return 0.0


def max_plane_internal_chord_mm(mask: np.ndarray,
                                affine: np.ndarray,
                                fixed_axis: int):
    vec_row, vec_col = inplane_vectors(affine, fixed_axis)
    best = 0.0

    for k in range(mask.shape[fixed_axis]):
        sl = extract_slice(mask, fixed_axis, k)

        if np.count_nonzero(sl) == 0:
            continue

        d_mm = max_internal_chord_slice_mm(sl, vec_row, vec_col)

        if d_mm > best:
            best = d_mm

    return best


def calculate_metrics(mask: np.ndarray, affine: np.ndarray):
    voxel_volume_mm3 = float(abs(np.linalg.det(affine[:3, :3])))
    foreground_voxels = int(np.count_nonzero(mask))

    volume_mm3 = foreground_voxels * voxel_volume_mm3
    volume_cm3 = volume_mm3 / 1000.0

    if foreground_voxels == 0:
        axial_mm = sagittal_mm = coronal_mm = 0.0
    else:
        axial_mm = max_plane_internal_chord_mm(mask, affine, fixed_axis=2)
        sagittal_mm = max_plane_internal_chord_mm(mask, affine, fixed_axis=0)
        coronal_mm = max_plane_internal_chord_mm(mask, affine, fixed_axis=1)

    axial_cm = axial_mm / 10.0
    sagittal_cm = sagittal_mm / 10.0
    coronal_cm = coronal_mm / 10.0

    plane_diameters = {
        "axial": axial_cm,
        "sagittal": sagittal_cm,
        "coronal": coronal_cm,
    }

    maximum_cm = max(plane_diameters.values())

    max_planes = [
        plane
        for plane, diameter in plane_diameters.items()
        if np.isclose(diameter, maximum_cm, rtol=1e-9, atol=1e-12)
    ]

    return {
        "volume_mm3": volume_mm3,
        "volume_cm3": volume_cm3,
        "max_axial_diameter_cm": axial_cm,
        "max_sagittal_diameter_cm": sagittal_cm,
        "max_coronal_diameter_cm": coronal_cm,
        "max_diameter_cm": maximum_cm,
        "max_diameter_plane": ";".join(max_planes),
    }


def nifti_files(folder: Path):
    files = list(folder.glob("*.nii")) + list(folder.glob("*.nii.gz"))
    return sorted(set(files), key=lambda p: p.name.lower())


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Calculate volume and maximum contour-to-contour INTERNAL CHORD "
            "diameters for post-processed NIfTI tumor masks."
        )
    )
    parser.add_argument(
        "folder",
        help="Folder containing post-processed .nii or .nii.gz masks",
    )
    args = parser.parse_args()

    folder = Path(args.folder)

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")

    files = nifti_files(folder)
    if not files:
        raise RuntimeError(f"No .nii or .nii.gz files found in: {folder}")

    output_csv = folder / OUTPUT_CSV_NAME

    fieldnames = [
        "filename",
        "volume_mm3",
        "volume_cm3",
        "max_axial_diameter_cm",
        "max_sagittal_diameter_cm",
        "max_coronal_diameter_cm",
        "max_diameter_cm",
        "max_diameter_plane",
    ]

    rows = []

    print(f"Found {len(files)} mask(s).")
    print(
        "Calculating contour-to-contour INTERNAL CHORD diameters "
        "(no convex hull / no alpha shape)..."
    )

    for i, path in enumerate(files, start=1):
        try:
            mask, affine = load_mask_canonical(path)
            metrics = calculate_metrics(mask, affine)

            row = {
                "filename": path.name,
                "volume_mm3": round(metrics["volume_mm3"], 3),
                "volume_cm3": round(metrics["volume_cm3"], 6),
                "max_axial_diameter_cm":
                    round(metrics["max_axial_diameter_cm"], 4),
                "max_sagittal_diameter_cm":
                    round(metrics["max_sagittal_diameter_cm"], 4),
                "max_coronal_diameter_cm":
                    round(metrics["max_coronal_diameter_cm"], 4),
                "max_diameter_cm":
                    round(metrics["max_diameter_cm"], 4),
                "max_diameter_plane":
                    metrics["max_diameter_plane"],
            }

            rows.append(row)

            print(
                f"[{i}/{len(files)}] {path.name}: "
                f"V={row['volume_cm3']:.3f} cm^3, "
                f"Ax={row['max_axial_diameter_cm']:.3f} cm, "
                f"Sag={row['max_sagittal_diameter_cm']:.3f} cm, "
                f"Cor={row['max_coronal_diameter_cm']:.3f} cm, "
                f"Max={row['max_diameter_cm']:.3f} cm "
                f"({row['max_diameter_plane']})"
            )

        except Exception as exc:
            print(f"[{i}/{len(files)}] FAILED: {path.name} ({exc})")

    with output_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print()
    print("Done. Results written to:")
    print(output_csv)


if __name__ == "__main__":
    main()
