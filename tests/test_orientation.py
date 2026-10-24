"""Synthetic regression tests for anatomical references and NIfTI storage order."""
import importlib.util
import itertools
from pathlib import Path
import sys
import tempfile
import unittest

import nibabel as nib
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
import vs_false_positive_correction as correction
import calculate_mask_metrics_internal_chord_contour as measurement


def variants():
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((-1, 1), repeat=3):
            yield np.array(list(zip(perm, signs)), dtype=float)


def reorient(data, affine, orientation):
    return (
        nib.orientations.apply_orientation(data, orientation),
        affine @ nib.orientations.inv_ornt_aff(orientation, data.shape),
    )


def save(path, data, affine):
    img = nib.Nifti1Image(data.astype(np.uint8), affine)
    img.header.set_xyzt_units("mm")
    img.set_qform(affine, code=2)
    img.set_sform(affine, code=4)
    nib.save(img, str(path))


def oblique_affine():
    angle = np.deg2rad(27)
    c, s = np.cos(angle), np.sin(angle)
    affine = np.eye(4)
    affine[:3, :3] = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]]) @ np.diag([1.2, 0.9, 2.0])
    affine[:3, 3] = [-15.3, 7.1, 20.4]
    return affine


class AnatomicalReferenceTests(unittest.TestCase):
    def test_reversed_z_max_index_is_inferior(self):
        bs = np.zeros((3, 3, 12), dtype=np.int16)
        bs[1, 1, [3, 8]] = 3
        affine = np.diag([1., 1., -2., 1.])
        affine[2, 3] = 30
        self.assertEqual(np.where(bs == 3)[2].max(), 8)
        self.assertEqual(correction.z_medulla_max(bs, affine), 3)
        self.assertEqual(correction.world_z_extreme(bs, affine, (3,), "superior"), 24.)

    def test_oblique_superior_endpoint_is_not_maximum_slice_index(self):
        bs = np.zeros((12, 3, 13), dtype=np.int16)
        bs[0, 1, 7] = 3
        bs[10, 1, 5] = 3
        affine = np.eye(4)
        affine[2, 0] = .5
        self.assertEqual(nib.aff2axcodes(affine), ("R", "A", "S"))
        self.assertEqual(correction.z_medulla_max(bs, affine), 5)
        bs[10, 1, 9] = 2
        bs[0, 1, 11] = 2
        self.assertEqual(correction.anatomical_extreme_slice(bs, affine, 2, "inferior"), 11)
        self.assertEqual(correction.z_medulla_pons_overlap(bs, affine), 8)

    def test_shared_slice_median_and_integer_conversion_preserved(self):
        bs = np.zeros((4, 4, 12), dtype=np.int16)
        bs[1, 1, 3:7] = 3
        bs[2, 2, 5:9] = 2
        self.assertEqual(correction.z_medulla_pons_overlap(bs, np.eye(4)), 5)

    def test_missing_reference_label_rejected(self):
        with self.assertRaises(RuntimeError):
            correction.z_medulla_max(np.zeros((3, 3, 3)), np.eye(4))

    def test_canonical_roundtrip_all_storage_orientations(self):
        data = np.arange(5*7*9).reshape(5, 7, 9)
        affine = oblique_affine()
        for orientation in variants():
            variant, variant_affine = reorient(data, affine, orientation)
            working, work_affine, inverse = correction.canonical_working_view(variant, variant_affine)
            np.testing.assert_array_equal(working, data)
            np.testing.assert_allclose(work_affine, affine, atol=1e-12)
            np.testing.assert_array_equal(nib.orientations.apply_orientation(working, inverse), variant)

    def test_standard_fallback_uses_anatomical_inferior_extent(self):
        mask = np.zeros((16, 5, 16), bool)
        mask[12:14, 1, 7:9] = True
        mask[0:2, 3, 9:11] = True
        affine = np.eye(4)
        affine[2, 0] = .5
        labeled, n, slices = correction.connected_components(mask)
        keep = correction.choose_component_complete(slices, labeled, 6, 5, affine, 5.)
        self.assertEqual(keep, int(labeled[0, 3, 9]))
        # The old minimum array-index rule would select the other component.
        old = min(range(1, n+1), key=lambda label: abs(slices[label-1][2].start-5))
        self.assertNotEqual(keep, old)

    def test_invalid_and_non_3d_geometry_rejected(self):
        bad = np.eye(4); bad[2] = 0
        with self.assertRaises(ValueError):
            correction.canonical_working_view(np.zeros((3, 3, 3)), bad)
        with self.assertRaises(ValueError):
            correction.canonical_working_view(np.zeros((3, 3, 3, 2)), np.eye(4))


class CaseProcessingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tumor = self.root / "tumor.nii.gz"
        self.brain = self.root / "brain.nii.gz"
        self.out = self.root / "out.nii.gz"

    def scenario(self, mode):
        tumor = np.zeros((15, 13, 17), np.uint8)
        tumor[6:8, 2:4, 4:9] = 1
        tumor[0:2, 9:11, 4:9] = 1
        bs = np.zeros(tumor.shape, np.int16)
        if mode == "complete":
            bs[7, 6, 2:6] = 3
            bs[7, 7, 5:10] = 2
        elif mode == "complete_no_overlap":
            bs[7, 6, 2:5] = 3
            bs[7, 7, 8:11] = 2
        elif mode == "standard_fallback":
            bs[7, 6, 2:6] = 3
            bs[7, 7, 8:11] = 2
            tumor[:] = 0
            tumor[6:8, 2:4, 10:13] = 1
            tumor[0:2, 9:11, 14:16] = 1
        else:
            labels = {"pons": [2], "midbrain": [1], "medulla": [3],
                      "midbrain_medulla": [1, 3], "midbrain_pons": [1, 2]}[mode]
            for j, label in enumerate(labels):
                bs[7, 6+j, 5+j:8+j] = label
        return tumor, bs

    def test_correction_all_48_orientations_both_branches_and_oblique(self):
        modes = ["complete", "complete_no_overlap", "standard_fallback", "pons",
                 "midbrain", "medulla", "midbrain_medulla", "midbrain_pons"]
        for affine in [np.diag([1.2, .9, 2., 1.]), oblique_affine()]:
            for mode in modes:
                tumor, bs = self.scenario(mode)
                save(self.tumor, tumor, affine); save(self.brain, bs, affine)
                message = correction.process_case(self.tumor, self.brain, self.out)
                self.assertIn("corrected", message, (mode, message))
                baseline = np.asarray(nib.load(self.out).dataobj)
                expected = tumor.copy(); expected[:2] = 0
                np.testing.assert_array_equal(baseline, expected, err_msg=mode)
                for orientation in variants():
                    with self.subTest(mode=mode, orientation=orientation.tolist()):
                        tv, av = reorient(tumor, affine, orientation)
                        bv, _ = reorient(bs, affine, orientation)
                        save(self.tumor, tv, av); save(self.brain, bv, av)
                        message = correction.process_case(self.tumor, self.brain, self.out)
                        self.assertIn("corrected", message)
                        output = nib.load(self.out)
                        predicted, out_affine, _ = correction.canonical_working_view(np.asarray(output.dataobj), output.affine)
                        np.testing.assert_array_equal(predicted, baseline)
                        np.testing.assert_allclose(output.affine, nib.load(self.tumor).affine, atol=1e-6)
                        self.assertEqual(output.shape, tv.shape)
                        self.assertEqual(int(output.header['qform_code']), 2)
                        self.assertEqual(int(output.header['sform_code']), 4)
                        self.assertEqual(output.header.get_xyzt_units()[0], "mm")

    def test_unchanged_cases_preserve_original_file_bytes(self):
        tumor, bs = self.scenario("complete")
        cases = ["single", "missing", "empty_brain", "shape", "affine"]
        for case in cases:
            with self.subTest(case=case):
                current = tumor.copy()
                if case == "single": current[:2] = 0
                save(self.tumor, current, np.eye(4))
                if self.brain.exists(): self.brain.unlink()
                if case == "empty_brain": save(self.brain, bs*0, np.eye(4))
                elif case == "shape": save(self.brain, bs[:-1], np.eye(4))
                elif case == "affine":
                    other = np.eye(4); other[0, 3] = 10
                    save(self.brain, bs, other)
                elif case != "missing": save(self.brain, bs, np.eye(4))
                self.assertIn("unchanged", correction.process_case(self.tumor, self.brain, self.out))
                self.assertEqual(self.tumor.read_bytes(), self.out.read_bytes())

    def test_empty_tumor_reports_failure_without_new_output(self):
        save(self.tumor, np.zeros((3, 4, 5)), np.eye(4))
        self.assertIn("failed", correction.process_case(self.tumor, self.brain, self.out))
        self.assertFalse(self.out.exists())

    def test_sheared_image_preserves_original_affine_and_voxels(self):
        tumor, bs = self.scenario("complete")
        affine = np.eye(4); affine[2, 0] = .4
        save(self.tumor, tumor, affine); save(self.brain, bs, affine)
        self.assertIn("corrected", correction.process_case(self.tumor, self.brain, self.out))
        output = nib.load(self.out)
        np.testing.assert_allclose(output.affine, nib.load(self.tumor).affine)
        self.assertTrue(np.all(np.asarray(output.dataobj) <= tumor))


class MeasurementOrientationTests(unittest.TestCase):
    def test_loader_measurements_invariant_under_all_storage_orientations(self):
        mask = np.zeros((5, 6, 7), np.uint8)
        mask[1:4, 2:5, 1:6] = 1
        for affine in [np.diag([1.2, .9, 2., 1.]), oblique_affine()]:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "mask.nii.gz"
                save(path, mask, affine)
                canonical, canonical_affine = measurement.load_mask_canonical(path)
                reference = measurement.calculate_metrics(canonical, canonical_affine)
                for orientation in variants():
                    variant, variant_affine = reorient(mask, affine, orientation)
                    save(path, variant, variant_affine)
                    data, resolved_affine = measurement.load_mask_canonical(path)
                    metrics = measurement.calculate_metrics(data, resolved_affine)
                    for key in ["volume_cm3", "max_axial_diameter_cm", "max_sagittal_diameter_cm", "max_coronal_diameter_cm", "max_obliquity_degrees"]:
                        self.assertAlmostEqual(metrics[key], reference[key], places=6)
                self.assertEqual(reference["measurement_plane_basis"], "RAS-reoriented acquisition planes")
                if affine[0, 2] != 0:
                    self.assertGreater(reference["max_obliquity_degrees"], 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
