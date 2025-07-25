#!/usr/bin/env python3
"""
correct_vs_mask.py  •  2025-07-25

Input
-----
--tumor_mask      : binary mask that may contain VS + false positives
--brainstem_mask  : label map (1 = midbrain, 2 = pons, 3 = medulla)
--output          : path for corrected binary mask

Logic
-----
1.  Find z_medulla_max  ……  most-superior slice that still contains medulla
2.  Find all z where **both** medulla & pons are present – take median → z_medulla_pons_med
    → define IAC z-range  [z_medulla_pons_med , z_medulla_max)
3.  Label connected components in tumor mask:
      • keep every component whose z-extent intersects either end-point of that range
      • if ≥1 components satisfy → pick the one whose x-centroid is closest to mid-line
      • else                      → pick the component whose lower-z (z0) is nearest z_medulla_max
4.  Save cleaned mask (uint8, 1 = kept component)
"""

import argparse
import numpy as np
import nibabel as nib
import scipy.ndimage as ndi
from pathlib import Path


def load_bool(path):
    img = nib.load(str(path))
    return img.get_fdata().astype(bool), img


def load_int(path):
    img = nib.load(str(path))
    return img.get_fdata().astype(np.int16)


# -------------------------------------------------------------------- brain-stem helpers
def z_medulla_max(bs: np.ndarray) -> int:
    zs = np.where(bs == 3)[2]
    if zs.size == 0:
        raise RuntimeError("No medulla voxels (label 3)!")
    return zs.max()


def z_medulla_pons_overlap(bs: np.ndarray) -> int:
    # slices that contain at least one voxel of BOTH medulla (3) and pons (2)
    z_med = np.unique(np.where(bs == 3)[2])
    z_pon = np.unique(np.where(bs == 2)[2])
    overlap = np.intersect1d(z_med, z_pon)
    if overlap.size == 0:
        # fall back to midpoint between pons & medulla maxima
        return int(0.5 * (z_med.max() + z_pon.min()))
    return int(np.median(overlap))


# -------------------------------------------------------------------- tumour helpers
def connected_components(mask: np.ndarray):
    labeled, n = ndi.label(mask)
    slices = ndi.find_objects(labeled)  # list index 0 corresponds to label 1
    return labeled, n, slices


def centroid_x(labeled, label_id):
    coords = ndi.center_of_mass(np.ones_like(labeled), labeled, [label_id])[0]
    return coords[0]  # x-coordinate


def choose_component(slices, labeled, iac_z_low, iac_z_high, mid_x):
    """
    • keep comps intersecting z in {iac_z_low, iac_z_high-1}
    • if multiple, choose centroid-x closest to mid_x
    • else pick closest-z comp
    """
    intersect = []
    for idx, sl in enumerate(slices, start=1):
        if sl is None:
            continue
        z0, z1 = sl[2].start, sl[2].stop - 1
        if (z0 <= iac_z_low <= z1) or (z0 <= iac_z_high - 1 <= z1):
            intersect.append(idx)

    if intersect:                                            # choose by x-distance
        dists = [abs(centroid_x(labeled, lb) - mid_x) for lb in intersect]
        return intersect[int(np.argmin(dists))]

    # --- none intersect: choose comp whose lower-bound z0 is closest to iac_z_high
    best, best_dist = None, np.inf
    for idx, sl in enumerate(slices, start=1):
        if sl is None:
            continue
        z0 = sl[2].start
        dist = abs(z0 - iac_z_high)
        if dist < best_dist:
            best, best_dist = idx, dist
    return best


# -------------------------------------------------------------------- main
def main(tumor_path: Path, brain_path: Path, out_path: Path):
    tumor_mask, tumor_img = load_bool(tumor_path)
    brainstem = load_int(brain_path)

    if tumor_mask.shape != brainstem.shape:
        raise ValueError("Tumor and brain-stem masks differ in shape!")

    z_max = z_medulla_max(brainstem)
    z_med = z_medulla_pons_overlap(brainstem)
    print(f"z_medulla_max = {z_max + 1} ,  z_medulla-pons_median = {z_med + 1}") # Add one unit to convert python indexes to MRI coordinates
    iac_low, iac_high = z_med, z_max

    labeled, n_comp, slcs = connected_components(tumor_mask)
    if n_comp == 0:
        raise RuntimeError("Tumor mask is empty!")

    mid_x = tumor_mask.shape[0] / 2.0
    keep = choose_component(slcs, labeled, iac_low, iac_high, mid_x)
    print(f"Keeping component #{keep} of {n_comp}")

    clean = (labeled == keep).astype(np.uint8)
    nib.save(nib.Nifti1Image(clean, tumor_img.affine, tumor_img.header), out_path)
    print("Saved →", out_path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tumor_mask",     required=True)
    ap.add_argument("--brainstem_mask", required=True)
    ap.add_argument("--output",         required=True)
    a = ap.parse_args()
    main(Path(a.tumor_mask), Path(a.brainstem_mask), Path(a.output))
