"""Calculate four segmentation metrics for same-named NIfTI mask pairs.

Usage:
    python dice_rve_assd_hd95_calculation.py --prediction PRED_FOLDER \
        --manual MANUAL_FOLDER --out OUTPUT_FOLDER

Dependencies: numpy, nibabel, SimpleITK, scipy.

Only .nii and .nii.gz files directly inside each input folder are considered.
Masks are binarized as values > 0. Identical filenames are paired; images must
have the same 3D shape and affine (absolute tolerance 1e-5; no resampling).

Outputs:
    case_metrics.csv: DSC, absolute RVE (fraction, not percent), pooled ASSD
        (mm), and max-directed-percentile HD95 (mm), plus case status/errors.
    metric_descriptive_statistics.csv: one row per metric; sample SD (ddof=1),
        linearly interpolated quartiles, and counts of valid/missing values.

Metric functions are retained unchanged. In particular, the existing DSC
function returns 0 for two empty masks. RVE is undefined for an empty manual
mask; surface metrics are undefined if either surface is empty. Undefined or
failed values are blank in CSVs and excluded separately for each metric in
the summary; their counts and case errors remain visible.
An exit status of 1 means the CSVs were written but some cases were not OK.
"""

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
import nibabel as nib
import SimpleITK as sitk
from scipy.spatial import cKDTree

# ---------- METRIC FUNCTIONS ----------


def compute_surface_voxels(mask):
    """Six-face-neighbor contour voxel centers in physical LPS coordinates."""
    if mask.GetDimension() != 3:
        raise ValueError("Surface metrics require 3D masks.")
    surface = sitk.LabelContour(mask, fullyConnected=False)
    coords_zyx = np.argwhere(sitk.GetArrayFromImage(surface) > 0)
    if len(coords_zyx) == 0:
        return np.empty((0, 3), dtype=float)
    spacing = np.asarray(mask.GetSpacing(), dtype=float)
    origin = np.asarray(mask.GetOrigin(), dtype=float)
    direction = np.asarray(mask.GetDirection(), dtype=float).reshape(3, 3)
    return origin + (coords_zyx[:, ::-1] * spacing) @ direction.T


def _directed_surface_distances(mask1, mask2):
    """Exact nearest-neighbor distances; avoids a dense pairwise matrix."""
    surf1 = compute_surface_voxels(mask1)
    surf2 = compute_surface_voxels(mask2)
    if len(surf1) == 0 or len(surf2) == 0:
        raise ValueError("One of the masks has an empty surface.")
    d1 = cKDTree(surf2).query(surf1, k=1, eps=0)[0]
    d2 = cKDTree(surf1).query(surf2, k=1, eps=0)[0]
    return d1, d2


def compute_assd(mask1, mask2):
    """Pooled bidirectional ASSD in mm, weighted by surface-voxel count.

    ASSD = (sum(d1) + sum(d2)) / (len(d1) + len(d2)).
    Boundary voxel centers have equal weight. No surface-area weighting.
    Physical origin, direction, and anisotropic spacing are included.
    """
    d1, d2 = _directed_surface_distances(mask1, mask2)
    return float((d1.sum() + d2.sum()) / (d1.size + d2.size))


def compute_masd(mask1, mask2):
    """Legacy metric: equal-weight mean of the two directional means, in mm."""
    d1, d2 = _directed_surface_distances(mask1, mask2)
    return float((d1.mean() + d2.mean()) / 2.0)


def compute_hd95(mask1, mask2):
    """Larger of the directed 95th percentiles, in mm; linear interpolation."""
    d1, d2 = _directed_surface_distances(mask1, mask2)
    return float(max(np.percentile(d1, 95), np.percentile(d2, 95)))


def dice_coefficient(mask1_np, mask2_np):
    mask1 = mask1_np > 0
    mask2 = mask2_np > 0
    intersection = np.sum(mask1 & mask2)
    size1 = np.sum(mask1)
    size2 = np.sum(mask2)
    return (2.0 * intersection) / (size1 + size2) if (size1 + size2) > 0 else 0.0

def compute_volume(mask_path):
    img = sitk.ReadImage(mask_path)
    spacing = img.GetSpacing()
    voxel_volume = spacing[0] * spacing[1] * spacing[2]
    mask_array = sitk.GetArrayFromImage(img)
    binary_mask = (mask_array > 0).astype(np.float32)
    return np.sum(binary_mask) * voxel_volume

def compute_rve(manual_volume, seg_volume):
    if manual_volume == 0:
        return np.nan
    return abs(seg_volume - manual_volume) / manual_volume

# ---------- FOLDER INPUT / CSV OUTPUT ----------

METRIC_UNITS = {"DSC": "unitless", "RVE": "fraction", "ASSD_mm": "mm", "HD95_mm": "mm"}
CASE_COLUMNS = ["Case", "Filename", *METRIC_UNITS, "Status", "Error"]
SUMMARY_COLUMNS = [
    "Metric", "Unit", "N_total", "N_valid", "N_missing", "Mean", "SD",
    "Median", "Q1", "Q3", "IQR", "Min", "Max",
]


def nifti_files(folder):
    """Return same-filename lookup for NIfTI files, without recursing."""
    return {
        path.name: path
        for path in folder.iterdir()
        if path.is_file() and path.name.lower().endswith((".nii", ".nii.gz"))
    }


def case_name(filename):
    return filename[:-7] if filename.lower().endswith(".nii.gz") else filename[:-4]


def calculate_case(prediction_path, manual_path):
    """Validate a paired image grid, then call the retained metric functions."""
    manual_img = nib.load(str(manual_path))
    prediction_img = nib.load(str(prediction_path))
    if len(manual_img.shape) != 3 or len(prediction_img.shape) != 3:
        raise ValueError("Both masks must be 3D.")
    if manual_img.shape != prediction_img.shape:
        raise ValueError("Manual and predicted masks have different shapes.")
    if not np.allclose(manual_img.affine, prediction_img.affine, rtol=0, atol=1e-5):
        raise ValueError("Manual and predicted masks have incompatible affines.")

    manual_np = np.asanyarray(manual_img.dataobj)
    prediction_np = np.asanyarray(prediction_img.dataobj)
    if not np.isfinite(manual_np).all() or not np.isfinite(prediction_np).all():
        raise ValueError("Masks contain non-finite voxel values.")

    values = {
        "DSC": float(dice_coefficient(manual_np, prediction_np)),
        "RVE": float(compute_rve(
            compute_volume(str(manual_path)), compute_volume(str(prediction_path))
        )),
        "ASSD_mm": np.nan,
        "HD95_mm": np.nan,
    }
    errors = []
    if not np.isfinite(values["RVE"]):
        errors.append("RVE undefined: manual mask is empty.")

    manual_mask = sitk.ReadImage(str(manual_path)) > 0
    prediction_mask = sitk.ReadImage(str(prediction_path)) > 0
    for metric, function in [("ASSD_mm", compute_assd), ("HD95_mm", compute_hd95)]:
        try:
            values[metric] = function(prediction_mask, manual_mask)
        except ValueError as exc:
            errors.append(f"{metric}: {exc}")
    return values, errors


def descriptive_statistics(results):
    """Use finite case values per metric; SD is the sample SD."""
    summary = []
    for metric, unit in METRIC_UNITS.items():
        values = np.asarray([row[metric] for row in results], dtype=float)
        values = values[np.isfinite(values)]
        row = {
            "Metric": metric, "Unit": unit, "N_total": len(results),
            "N_valid": len(values), "N_missing": len(results) - len(values),
        }
        for statistic in SUMMARY_COLUMNS[5:]:
            row[statistic] = np.nan
        if len(values):
            q1, median, q3 = np.percentile(values, [25, 50, 75])
            row.update({
                "Mean": float(np.mean(values)),
                "SD": float(np.std(values, ddof=1)) if len(values) > 1 else np.nan,
                "Median": float(median), "Q1": float(q1), "Q3": float(q3),
                "IQR": float(q3 - q1),
                "Min": float(np.min(values)), "Max": float(np.max(values)),
            })
        summary.append(row)
    return summary


def write_csv(path, columns, rows):
    """Keep numeric precision; represent undefined numeric values as blanks."""
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                key: "" if isinstance(value, (float, np.floating)) and not np.isfinite(value)
                else value
                for key, value in row.items()
            })


def run_folders(prediction_folder, manual_folder, output_folder):
    prediction_folder = Path(prediction_folder).expanduser().resolve()
    manual_folder = Path(manual_folder).expanduser().resolve()
    output_folder = Path(output_folder).expanduser().resolve()
    for label, folder in [("Prediction", prediction_folder), ("Manual", manual_folder)]:
        if not folder.is_dir():
            raise ValueError(f"{label} folder does not exist: {folder}")

    predictions = nifti_files(prediction_folder)
    manuals = nifti_files(manual_folder)
    if not predictions.keys() & manuals.keys():
        raise ValueError("No same-named NIfTI mask pairs were found in the input folders.")

    filenames = sorted(predictions.keys() | manuals.keys(), key=lambda name: (name.casefold(), name))
    results = []
    print(f"Processing {len(filenames)} case file(s)...")
    for filename in filenames:
        row = {
            "Case": case_name(filename), "Filename": filename,
            **{metric: np.nan for metric in METRIC_UNITS},
            "Status": "OK", "Error": "",
        }
        if filename not in predictions:
            row.update(Status="ERROR", Error="Prediction mask is missing.")
        elif filename not in manuals:
            row.update(Status="ERROR", Error="Manual mask is missing.")
        else:
            try:
                values, errors = calculate_case(predictions[filename], manuals[filename])
                row.update(values)
                if errors:
                    row.update(Status="PARTIAL", Error="; ".join(errors))
            except Exception as exc:
                row.update(Status="ERROR", Error=f"{type(exc).__name__}: {exc}")
        results.append(row)
        if row["Status"] == "OK":
            print(
                f"{row['Case']}: DSC={row['DSC']:.6f}, RVE={row['RVE']:.6f}, "
                f"ASSD={row['ASSD_mm']:.6f} mm, HD95={row['HD95_mm']:.6f} mm"
            )
        else:
            print(f"{row['Case']}: {row['Status']} - {row['Error']}")

    output_folder.mkdir(parents=True, exist_ok=True)
    case_csv = output_folder / "case_metrics.csv"
    summary_csv = output_folder / "metric_descriptive_statistics.csv"
    write_csv(case_csv, CASE_COLUMNS, results)
    write_csv(summary_csv, SUMMARY_COLUMNS, descriptive_statistics(results))
    n_flagged = sum(row["Status"] != "OK" for row in results)
    print(f"Saved {case_csv}")
    print(f"Saved {summary_csv}")
    print(f"{len(results) - n_flagged} OK; {n_flagged} flagged case(s).")
    return 1 if n_flagged else 0


def main():
    parser = argparse.ArgumentParser(
        description="Calculate DSC, absolute RVE, pooled ASSD and HD95 for same-named masks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "RVE is an absolute fraction (0.10 = 10%); ASSD and HD95 are in mm.\n"
            "Inputs are flat folders of .nii/.nii.gz masks; no resampling is performed.\n"
            "Writes case_metrics.csv and metric_descriptive_statistics.csv."
        ),
    )
    parser.add_argument("--prediction", required=True, type=Path, help="Prediction mask folder.")
    parser.add_argument("--manual", required=True, type=Path, help="Manual/reference mask folder.")
    parser.add_argument("--out", required=True, type=Path, help="Output folder for both CSVs.")
    args = parser.parse_args()
    try:
        return run_folders(args.prediction, args.manual, args.out)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    sys.exit(main())
