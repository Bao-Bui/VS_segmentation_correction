# Acquisition identity, crossMoDA aliases, and MC-RC / London overlap

**Reviewed: October 16, 2026.**

These derived tables distinguish shared subjects, repeated MRI acquisitions, and alternate annotations. Image identity was established using the official TCIA mapping, canonical-voxel fingerprints, and targeted visual review of defacing variants. Identity confirmation does not establish equivalent segmentations or completed eligibility QC.

## Tables

| File | Rows | One row represents |
|---|---:|---|
| [mc_rc_l_sc_gk_subject_overlap.csv](mc_rc_l_sc_gk_subject_overlap.csv) | 58 | One subject shared between London and MC-RC, with modality-specific counts |
| [mc_rc_l_sc_gk_series_overlap.csv](mc_rc_l_sc_gk_series_overlap.csv) | 187 | An MC-RC scan from a shared subject |
| [mc_rc_l_sc_gk_exact_duplicate_series.csv](mc_rc_l_sc_gk_exact_duplicate_series.csv) | 15 | A confirmed duplicated acquisition: eight officially mapped plus seven newly established |
| [london_t1_crosswalk.csv](london_t1_crosswalk.csv) | 242 | One London TCIA subject and its challenge/MC-RC acquisition aliases |
| [tilburg_2022_2023_crosswalk.csv](tilburg_2022_2023_crosswalk.csv) | 105 | An exact voxel match between the Tilburg source releases |
| [ukm2023_mc_rc_crosswalk.csv](ukm2023_mc_rc_crosswalk.csv) | 43 | A UKM source T1 acquisition matched to MC-RC, with annotation availability |
| [london_mc_rc_t1_duplicate_acquisitions.csv](london_mc_rc_t1_duplicate_acquisitions.csv) | 14 | A duplicated T1 acquisition with matching evidence |
| [mc_rc_t1_metadata_recovered.csv](mc_rc_t1_metadata_recovered.csv) | 124 | An MC-RC T1 scan with public identifiers and annotation availability across releases |

The [summary JSON](identity_audit_summary.json) records reconciled counts.

## Findings

- London–MC overlap: **14 T1 and one T2 acquisitions**. TCIA's official table covers seven T1 and one T2; the seven additional T1 relationships were established through matching central patches and visual confirmation of different defacing.
- The 58 shared subjects contribute 187 MC-RC scans. After the identified duplicates are excluded, **172 scans remain: 48 T1 and 124 T2**, including 103 TCIA native masks (26 T1 and 77 T2). This is a count of scans not identified as duplicates, not proof that every remaining T2 scan has undergone image matching.
- **57** shared subjects have another MC-RC acquisition. **VS-SEG-126 has only its duplicated T1 acquisition.**
- London source aliases: **105/105** source scans from the 2022 package, and **79/79** from 2023, match the TCIA reference images exactly after canonical axis reorientation.
- Tilburg source aliases: **105/105** source scans match across 2022/2023; IDs are shuffled.
- UKM source aliases: **43/43** match MC-RC, comprising 40 exact full-voxel matches and three visual confirmations.
- UKM's 43 acquisitions include **19 already having TCIA native T1 masks** and **24 that gain a public T1 annotation through crossMoDA**. All 24 have same-study T2 scans with public masks.
- MC-RC/UKM T1 union: **88 acquisitions / 67 subjects**.
- London + Tilburg + original MC-RC/UKM: **421 T1 acquisitions before eligibility and segmentation QC**.
- Bilateral cochlea releases: **253 annotation records on 251 acquisitions**; UKM 21/London126 and UKM24/London095 repeat acquisitions.
- MC-RC2 and UCSD were not included in the fingerprint archive. The expanded reported candidate pool is conditional on their release counts and local checks.

## Definitions and evidence

### Official versus derived duplicate relationships

- official_tcia_overlap_mapping preserves membership in TCIA's original eight-series table.
- same_acquisition_as_london_identified identifies confirmed acquisition overlap. The evidence field distinguishes official mapping from visual confirmation.
- duplicate_confirmed_by_image_matching_and_visual_review records the seven additional T1 relationships, not a claim that TCIA has already amended its table.
- not_identified_as_duplicate_in_current_audit leaves other scans unmerged. Absence of an image match is not universal proof of uniqueness.
- The historical filename exact_duplicate_series refers to the same acquisition, not byte-identical files or voxel arrays. Different defacing can change voxels.

### Public annotation availability

- Native TCIA mask fields describe the final repaired TCIA product only.
- public_t1_vs_annotation_available in the 124-row inventory includes either a native TCIA T1 annotation or a matched UKM source annotation.
- UKM VS subregions and cochlea share a multiclass label product. Whole-VS extraction requires the documented tumor-class union; cochlea must remain separate.
- A matched acquisition is not a completed mask transfer. Each annotation should remain paired with its release's reference image until geometry and labels are validated.
- same_study_t1_t2 and same-study T2 series keys use the MC-RC Study Instance UID, not merely matching calendar dates.
- Modalities counted within with_masks/without_masks folders do not describe all modalities acquired for the subject or examination.

### Matching methods

The source fingerprint audit analyzed 803 selected T1 images without reading errors. Complete scaled canonical float64 voxel arrays were hashed after axis flips/permutations, without resampling. Candidate patches comprised nonoverlapping non-flat central regions.

All 14 London–MC T1 pairs share 27/27 sampled central patches. Seven are supported by the official mapping; the other seven were reviewed visually on October 16, 2026 and confirmed as the same acquisition with different defacing.

UKM 2, 6, and 35 had matching geometry but no exact matching central patches. Targeted visual review confirmed them as the same MC-RC acquisitions with different defacing; their match method remains explicitly visual rather than being relabeled as full-voxel equality.

CrossMoDA image identity does not establish original drawing modality or annotation equivalence. Anatomical mask review and contrast/coverage eligibility remain separate.

### IDs, dates, paths, and geometry

- Dates are archive-released de-identified study/series dates, not independently verified clinical calendar dates.
- MC-RC Study/Series Instance UIDs are retained. London Series Instance UIDs are populated where supplied by the official mapping; missing values are not invented.
- Series keys use the converter's modality prefix plus the first 12 hexadecimal characters of SHA-256(Series Instance UID).
- London source filenames in the 2022 package retain the crossmoda2021_ldn prefix.
- All image and label paths are relative to their original release roots; no workstation paths are included.
- Two exact voxel pairs, UKM3/MC-RC-079 and UKM16/MC-RC-099, have small cross-release affine differences (maximum corner displacement approximately 0.00455 mm and 0.00467 mm). Use the supplied reference image with its annotation.
- Subject-level native-mask counts remain TCIA-only; they should not be mistaken for the combined annotation availability fields in the 124-row T1 table.

## Sources and provenance

1. TCIA's series_overlap_between_VS-MC-RC_and_-VS-SEG.csv supplied the original eight acquisition correspondences.
2. The released Vestibular-Schwannoma-MC-RC_NIfTI-segmentation-info3.csv and conversion inventory supplied MRI metadata and public study/series UIDs.
3. The final repaired pair-validation inventory established the 301 native TCIA masks. Earlier rejection statuses were not used as final mask availability.
4. public_t1_identity_audit_20261015_152439.zip supplied image fingerprints, relative paths, and geometry across TCIA London, TCIA MC-RC, and the 2022/2023 source releases.
5. Targeted visual review on October 16, 2026 confirmed the seven additional London–MC pairs and UKM2/6/35 as defacing variants of the same acquisitions.

The ambiguous MC inventory links in the original fingerprint CSV were recovered uniquely by matching the SHA-256-derived series key to the original Series Instance UID. All 124 T1 metadata joins and final native-mask statuses reconciled.

Official sources: [London TCIA](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/), [MC-RC TCIA](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/), [official overlap explanation](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=157287455), [crossMoDA 2022](https://zenodo.org/records/6504722), [crossMoDA 2023](https://www.synapse.org/Synapse:syn51236108).

Cite the actual source dataset releases and identify these files as derived acquisition/availability summaries. Licenses differ between TCIA and challenge products; image identity does not replace either release's terms.
