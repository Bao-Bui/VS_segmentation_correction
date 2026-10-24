#!/usr/bin/env python3
"""
Post-process a *folder* of auto-segmented vestibular-schwannoma masks by
removing false-positive components, using each patient’s brain-stem
labels (midbrain=1, pons=2, medulla=3) as anatomical reference.

Folder layout (example)
-----------------------
tumor_output_folder/
    VS_001.nii.gz
    VS_002.nii.gz
    ...
brainstem_output_folder/
    VS_001.nii.gz     
    VS_002.nii.gz
    ...
postprocess_folder/        
    VS_001.nii.gz
    VS_002.nii.gz
    ...

Correction policy
-----------------
1. If the raw VS mask contains exactly ONE connected component, do not run
   false-positive correction. Copy the raw mask unchanged to the output.

2. If the raw VS mask contains TWO OR MORE connected components:
   a. If pons and medulla are both present, use the original pons/medulla
      anatomical-reference logic.
   b. If that reference is incomplete, choose the component whose centroid
      is closest (in physical mm, in the left-right / superior-inferior plane)
      to the image midline and to an available brainstem boundary:
        - Medulla absent, pons present: use the most inferior point of the
          pons (label 2), regardless of whether midbrain is also present.
        - Medulla absent, pons absent, midbrain present: use the most inferior
          point of the midbrain (label 1).
        - Midbrain + medulla present, pons absent: use the midpoint between the
          most inferior midbrain point and the most superior medulla point.
        - Medulla only: use the most superior point of the medulla (label 3).
   c. Any other unusable brainstem pattern is left unchanged.

Both masks are processed in a losslessly reoriented RAS working view. No
interpolation or resampling is performed. The NIfTI affine determines physical
superior/inferior and left/right positions, including for oblique acquisitions.
The complete pathway still tests crossing of acquired reference slices. Its
medulla reference is the slice containing the physically most superior medulla
voxel center, which need not have the largest slice index in an oblique image.
Corrected masks are transformed back to the original tumor-mask storage order.
Distances assume affine spatial units are millimeters, as in the input NIfTIs.
"""

import argparse
import concurrent.futures as cf
import shutil
from pathlib import Path
from typing import Optional

import nibabel as nib
import numpy as np
import scipy.ndimage as ndi


# ─────────────────────────── Utility Loaders ────────────────────────────
def load_bool(path: Path):
    img = nib.load(str(path))
    return img.get_fdata().astype(bool), img


def load_int(path: Path):
    img = nib.load(str(path))
    return img.get_fdata().astype(np.int16), img


def copy_unchanged(src: Path, dst: Path):
    """Copy a raw NIfTI unchanged into the post-processed output folder."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def save_binary_mask(mask: np.ndarray, reference_img, out_path: Path):
    """Save a corrected binary mask on the raw tumor image geometry."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = reference_img.header.copy()
    header.set_data_dtype(np.uint8)
    nib.save(
        nib.Nifti1Image(mask.astype(np.uint8),
                        reference_img.affine,
                        header),
        str(out_path),
    )


# ───────────────────────── Brainstem Helpers ───────────────────────────
def canonical_working_view(data: np.ndarray, affine: np.ndarray):
    """Losslessly reorder/flip a 3D array toward RAS and return its inverse.

    RAS specifies axis ordering and direction. Oblique acquired planes remain
    oblique; anatomical extrema must still be computed with the affine.
    """
    affine = np.asarray(affine, dtype=float)
    if data.ndim != 3:
        raise ValueError(f"Expected a 3D mask, got shape {data.shape}")
    if (affine.shape != (4, 4) or not np.all(np.isfinite(affine))
            or not np.allclose(affine[3], [0, 0, 0, 1])
            or np.linalg.matrix_rank(affine[:3, :3]) != 3):
        raise ValueError("Mask has an invalid or singular spatial affine")
    native = nib.orientations.io_orientation(affine)
    ras = nib.orientations.axcodes2ornt(("R", "A", "S"))
    forward = nib.orientations.ornt_transform(native, ras)
    inverse = nib.orientations.ornt_transform(ras, native)
    working = nib.orientations.apply_orientation(data, forward)
    working_affine = affine @ nib.orientations.inv_ornt_aff(forward, data.shape)
    return working, working_affine, inverse


def anatomical_z_extreme(bs: np.ndarray, affine: np.ndarray,
                         labels, mode: str) -> Optional[tuple[float, int]]:
    """Return (world Z, acquired slice index) for an anatomical extremum.

    Inputs use the common RAS working view. Extrema refer to voxel centers.
    Lower world Z is inferior and higher world Z is superior. The slice index
    is axis 2 of the voxel attaining the extremum, not necessarily the maximum
    occupied slice index in an oblique image. Ties use the first voxel in array
    order. Return None when none of the requested labels is present.
    """
    voxels = np.argwhere(np.isin(bs, labels))
    if voxels.size == 0:
        return None
    world_z = nib.affines.apply_affine(affine, voxels)[:, 2]
    if mode == "superior":
        index = np.argmax(world_z)
    elif mode == "inferior":
        index = np.argmin(world_z)
    else:
        raise ValueError("mode must be 'inferior' or 'superior'")
    return float(world_z[index]), int(voxels[index, 2])


def z_medulla_max(bs: np.ndarray, affine: np.ndarray) -> int:
    """Slice containing the anatomically superior medulla voxel center.

    The legacy function name is retained, but maximum ARRAY index is no longer
    assumed to mean superior. Call on the common RAS working view.
    """
    extreme = anatomical_z_extreme(bs, affine, labels=(3,), mode="superior")
    if extreme is None:
        raise RuntimeError("No brainstem voxels for label 3")
    return extreme[1]


def z_medulla_pons_overlap(bs: np.ndarray, affine: np.ndarray,
                           medulla_superior_slice: Optional[int] = None) -> int:
    """Junction reference in the common RAS acquired-slice coordinates.

    Preserve the integer median of shared acquired slices. Without overlap,
    use the integer midpoint between the slices containing the physically
    superior medulla and physically inferior pons endpoints.
    """
    z_med = np.unique(np.where(bs == 3)[2])
    z_pon = np.unique(np.where(bs == 2)[2])
    if z_med.size == 0:
        raise RuntimeError("No medulla voxels (label 3) in brain-stem mask!")
    if z_pon.size == 0:
        raise RuntimeError("No pons voxels (label 2) in brain-stem mask!")
    overlap = np.intersect1d(z_med, z_pon)
    if overlap.size:
        return int(np.median(overlap))
    if medulla_superior_slice is None:
        medulla_superior_slice = z_medulla_max(bs, affine)
    _, pons_inferior = anatomical_z_extreme(bs, affine, (2,), "inferior")
    return int(0.5 * (medulla_superior_slice + pons_inferior))


def incomplete_brainstem_reference(bs: np.ndarray,
                                   affine: np.ndarray):
    """
    Choose a world-Z reference for an incomplete brainstem segmentation.

    Fallback hierarchy:
      1) Medulla absent, pons present (pons-only or midbrain+pons):
         use the most inferior world-Z of the PONS specifically.
      2) Medulla absent, pons absent, midbrain present:
         use the most inferior world-Z of the midbrain.
      3) Midbrain + medulla present, pons absent:
         use the midpoint between the most inferior midbrain world-Z and the
         most superior medulla world-Z.
      4) Medulla only:
         use the most superior world-Z of the medulla.

    This implements the intended "pons-midbrain complex" rule: if pons is
    available, pons defines the inferior boundary; midbrain is used only when
    pons is unavailable.
    """
    has_midbrain = np.any(bs == 1)
    has_pons = np.any(bs == 2)
    has_medulla = np.any(bs == 3)

    # No medulla: pons takes priority over midbrain. This includes pons-only
    # and midbrain+pons masks.
    if has_pons and (not has_medulla):
        target_z, _ = anatomical_z_extreme(bs, affine, labels=(2,), mode="inferior")
        return target_z, "inferior boundary of pons"

    # No pons or medulla: fall back to the inferior boundary of midbrain.
    if has_midbrain and (not has_pons) and (not has_medulla):
        target_z, _ = anatomical_z_extreme(bs, affine, labels=(1,), mode="inferior")
        return target_z, "inferior boundary of midbrain"

    # Pons missing, but both midbrain and medulla survived. Estimate the
    # missing pons level from the midpoint of the two adjacent boundaries.
    if has_midbrain and has_medulla and (not has_pons):
        midbrain_inf, _ = anatomical_z_extreme(
            bs, affine, labels=(1,), mode="inferior"
        )
        medulla_sup, _ = anatomical_z_extreme(
            bs, affine, labels=(3,), mode="superior"
        )
        target_z = 0.5 * (midbrain_inf + medulla_sup)
        return (
            target_z,
            "midpoint of inferior midbrain and superior medulla boundaries",
        )

    # Medulla-only fallback.
    if has_medulla and (not has_midbrain) and (not has_pons):
        target_z, _ = anatomical_z_extreme(bs, affine, labels=(3,), mode="superior")
        return target_z, "superior boundary of medulla"

    return None, "no usable brainstem labels"


# ───────────────────── Tumor Component Helpers ─────────────────────────
def connected_components(mask: np.ndarray):
    labeled, n = ndi.label(mask)
    slices = ndi.find_objects(labeled)
    return labeled, n, slices


def centroid_world_xz(labeled: np.ndarray,
                      label_id: int,
                      affine: np.ndarray):
    """Return component centroid as (world X, world Z), in mm."""
    centroid_vox = np.asarray(
        ndi.center_of_mass(
            np.ones_like(labeled, dtype=np.uint8), labeled, label_id
        ),
        dtype=float,
    )
    centroid_world = nib.affines.apply_affine(affine, centroid_vox)
    return float(centroid_world[0]), float(centroid_world[2])


def image_midline_world_x(shape, affine: np.ndarray) -> float:
    """
    World-X coordinate of the geometric center of the image volume.

    This preserves the old script's concept of 'image midline' while making
    the fallback robust to axis permutations/flips in the NIfTI affine.
    """
    center_vox = (np.asarray(shape, dtype=float) - 1.0) / 2.0
    center_world = nib.affines.apply_affine(affine, center_vox)
    return float(center_world[0])


def choose_component_complete(
    slices,
    labeled,
    pontomedullary_z,
    medulla_z,
    affine,
    medulla_z_world,
):
    """Preserve acquired-slice crossing, then rank with anatomical distances.

    Crossing candidates use centroid-to-image-center world-X distance. If
    none crosses either reference slice, retain the original inferior-boundary
    fallback using each component's minimum world Z relative to superior
    medulla world Z. This remains a one-dimensional fallback, not a combined
    centroid X-Z distance or shortest distance from the whole component.
    """
    midline_x_world = image_midline_world_x(labeled.shape, affine)
    z_lower, z_upper = sorted(
        (float(pontomedullary_z), float(medulla_z))
    )

    candidates = []

    for idx, sl in enumerate(slices, start=1):
        if sl is None:
            continue

        z0 = sl[2].start
        z1 = sl[2].stop - 1

        # Retain components crossing either reference level.
        if (z0 <= z_lower <= z1) or (z0 <= z_upper <= z1):
            candidates.append(idx)

    if candidates:
        return min(
            candidates,
            key=lambda lb: abs(
                centroid_world_xz(labeled, lb, affine)[0] - midline_x_world
            ),
        )

    # Preserve the inferior-boundary objective, using physical anatomy.
    best = None
    best_dist = np.inf

    for idx, sl in enumerate(slices, start=1):
        if sl is None:
            continue

        voxels_local = np.argwhere(labeled[sl] == idx)
        offset = np.array([axis_slice.start for axis_slice in sl])
        voxels = voxels_local + offset
        inferior_world_z = float(
            nib.affines.apply_affine(affine, voxels)[:, 2].min()
        )
        dist = abs(inferior_world_z - medulla_z_world)

        if dist < best_dist:
            best = idx
            best_dist = dist

    return best


def choose_component_incomplete(labeled: np.ndarray,
                                n_comp: int,
                                affine: np.ndarray,
                                midline_x_world: float,
                                target_z_world: float):
    """
    Choose the component whose centroid is nearest to BOTH:
      1) the image midline (world X), and
      2) the selected brainstem boundary (world Z).

    Distance is ordinary Euclidean distance in the X-Z plane, in millimeters,
    so left-right and superior-inferior offsets are weighted on the same
    physical scale.
    """
    best_label = None
    best_dist = np.inf

    for label_id in range(1, n_comp + 1):
        cx_world, cz_world = centroid_world_xz(labeled, label_id, affine)
        dist = np.hypot(
            cx_world - midline_x_world,
            cz_world - target_z_world,
        )
        if dist < best_dist:
            best_label = label_id
            best_dist = dist

    return best_label, float(best_dist)


# ───────────────────────── Single-Case Processing ──────────────────────
def process_case(tumor_path: Path, brain_path: Path, out_path: Path):
    try:
        # IMPORTANT: count tumor components BEFORE requiring a brainstem mask.
        tumor_mask, tumor_img = load_bool(tumor_path)
        tumor_working, working_affine, restore_orientation = (
            canonical_working_view(tumor_mask, tumor_img.affine)
        )
        labeled, n_comp, slcs = connected_components(tumor_working)

        if n_comp == 0:
            raise RuntimeError("Empty tumor mask")

        # Rule 1: one connected component => no correction at all.
        if n_comp == 1:
            copy_unchanged(tumor_path, out_path)
            return f"{tumor_path.name}  unchanged  (1 component)"

        # From here onward, correction is needed because n_comp >= 2.
        if not brain_path.exists():
            copy_unchanged(tumor_path, out_path)
            return (
                f"{tumor_path.name}  unchanged  "
                f"({n_comp} components; brainstem mask missing)"
            )

        brainstem, brain_img = load_int(brain_path)

        if tumor_mask.shape != brainstem.shape:
            copy_unchanged(tumor_path, out_path)
            return (
                f"{tumor_path.name}  unchanged  "
                f"({n_comp} components; shape mismatch with brainstem mask)"
            )

        if not np.allclose(tumor_img.affine, brain_img.affine, atol=1e-4):
            copy_unchanged(tumor_path, out_path)
            return (
                f"{tumor_path.name}  unchanged  "
                f"({n_comp} components; affine mismatch with brainstem mask)"
            )

        brainstem, brainstem_affine, _ = canonical_working_view(
            brainstem, brain_img.affine
        )
        if brainstem.shape != tumor_working.shape:
            raise RuntimeError("Inconsistent canonical tumor/brainstem geometry")

        has_pons = np.any(brainstem == 2)
        has_medulla = np.any(brainstem == 3)

        if has_pons and has_medulla:
            # Complete enough for the original correction pathway.
            medulla_z_world, medulla_z = anatomical_z_extreme(
                brainstem, brainstem_affine, labels=(3,), mode="superior"
            )
            pontomedullary_z = z_medulla_pons_overlap(
                brainstem, brainstem_affine, medulla_superior_slice=medulla_z
            )
            
            keep = choose_component_complete(
                slcs,
                labeled,
                pontomedullary_z,
                medulla_z,
                affine=working_affine,
                medulla_z_world=medulla_z_world,
            )

            mode = (
                "standard pons+medulla reference; RAS acquired slices "
                f"junction={pontomedullary_z}, medulla={medulla_z}; "
                f"superior medulla world Z={medulla_z_world:.3f} mm"
            )

        else:
            # Incomplete brainstem fallback.
            target_z_world, reference_name = incomplete_brainstem_reference(
                brainstem, brainstem_affine
            )

            if target_z_world is None:
                copy_unchanged(tumor_path, out_path)
                return (
                    f"{tumor_path.name}  unchanged  "
                    f"({n_comp} components; {reference_name})"
                )

            midline_x_world = image_midline_world_x(
                tumor_working.shape, working_affine
            )
            keep, distance_mm = choose_component_incomplete(
                labeled,
                n_comp,
                working_affine,
                midline_x_world,
                target_z_world,
            )
            mode = (
                f"incomplete brainstem: {reference_name}; "
                f"centroid distance={distance_mm:.1f} mm"
            )

        if keep is None:
            raise RuntimeError("Could not select a tumor component to preserve")

        cleaned_working = (labeled == keep).astype(np.uint8)
        cleaned = nib.orientations.apply_orientation(
            cleaned_working, restore_orientation
        )
        if cleaned.shape != tumor_mask.shape:
            raise RuntimeError("Failed to restore original tumor-mask geometry")
        save_binary_mask(cleaned, tumor_img, out_path)

        return (
            f"{tumor_path.name}  corrected  "
            f"({n_comp} -> 1 component; kept #{keep}; {mode})"
        )

    except Exception as e:
        return f"{tumor_path.name}  failed  ({e})"


# ──────────────────────────── Main ──────────────────────────────────────
def main(args):
    tumor_dir = Path(args.tumor)
    brain_dir = Path(args.brainstem)
    out_dir = Path(args.out)

    cases = []
    for tum_f in sorted(tumor_dir.glob("*.nii.gz")):
        pid = tum_f.name.replace(".nii.gz", "")
        brain_f = brain_dir / f"{pid}.nii.gz"
        out_f = out_dir / f"{pid}.nii.gz"

        # Include every tumor case. A brainstem mask is only required if the
        # raw tumor output actually has >=2 connected components.
        cases.append((tum_f, brain_f, out_f))

    if not cases:
        print("No tumor masks found.")
        return

    print(f"Processing {len(cases)} case(s)...")
    out_dir.mkdir(parents=True, exist_ok=True)

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for msg in ex.map(lambda t: process_case(*t), cases):
            print(msg)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Batch false-positive correction for VS masks"
    )
    ap.add_argument(
        "--tumor",
        required=True,
        help="Folder with raw VS+FP masks (*.nii.gz)",
    )
    ap.add_argument(
        "--brainstem",
        required=True,
        help="Folder with labelled brainstem masks (*.nii.gz)",
    )
    ap.add_argument(
        "--out",
        required=True,
        help="Destination folder for cleaned masks",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Parallel workers (default 1 = serial)",
    )
    main(ap.parse_args())

