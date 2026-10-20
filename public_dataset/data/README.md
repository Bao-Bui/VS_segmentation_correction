# Acquisition identity, crossMoDA aliases, and MC-RC / London overlap

**Reviewed: October 20, 2026.**

These derived tables distinguish shared subjects, repeated MRI acquisitions, and alternate annotations. Image identity was established using the official TCIA mapping, canonical-voxel fingerprints, and targeted visual review of defacing variants. Identity confirmation does not establish equivalent segmentations or completed eligibility QC.

## Tables

| File | Rows | One row represents |
|---|---:|---|
| [mc_rc_l_sc_gk_subject_overlap.csv](mc_rc_l_sc_gk_subject_overlap.csv) | 58 | One subject shared between London and MC-RC, with modality-specific counts |
| [mc_rc_l_sc_gk_series_overlap.csv](mc_rc_l_sc_gk_series_overlap.csv) | 187 | An MC-RC scan from a shared subject |
| [mc_rc_l_sc_gk_exact_duplicate_series.csv](mc_rc_l_sc_gk_exact_duplicate_series.csv) | 18 | A confirmed duplicated acquisition: eight officially mapped plus ten established by the repository audit |
| [london_t1_crosswalk.csv](london_t1_crosswalk.csv) | 242 | One London TCIA subject and its challenge/MC-RC acquisition aliases |
| [tilburg_2022_2023_crosswalk.csv](tilburg_2022_2023_crosswalk.csv) | 105 | An exact voxel match between the Tilburg source releases |
| [ukm2023_mc_rc_crosswalk.csv](ukm2023_mc_rc_crosswalk.csv) | 43 | A UKM source T1 acquisition matched to MC-RC, with annotation availability |
| [london_mc_rc_t1_duplicate_acquisitions.csv](london_mc_rc_t1_duplicate_acquisitions.csv) | 15 | A duplicated T1 acquisition with matching evidence |
| [mc_rc_t1_metadata_recovered.csv](mc_rc_t1_metadata_recovered.csv) | 124 | An MC-RC T1 scan with public identifiers and annotation availability across releases |
| [mc_rc_l_sc_gk_duplication_qc.csv](mc_rc_l_sc_gk_duplication_qc.csv) | 172 | A completed visual comparison from the previously unresolved shared-subject scans |
| [london_surgical_status.csv](london_surgical_status.csv) | 242 | One London reference scan, partial organizer metadata, and editable surgical/fat-graft QC fields |

The [summary JSON](identity_audit_summary.json) records reconciled counts.

## Findings

- London–MC overlap: **15 T1 and three T2 acquisitions**. TCIA's official table covers seven T1 and one T2. The repository audit establishes eight additional T1 and two additional T2 relationships.
- The October 20 completed review covered all 172 previously unresolved scans: **169 different acquisitions and three additional duplicates**. New duplicates are VS-SEG-094 T2, VS-SEG-172 T2, and VS-SEG-221 T1. Subject 221 has different axial slice coverage despite matching anatomy.
- The 58 shared subjects contribute 187 MC-RC scans. Excluding 18 identified duplicates leaves **169 scans: 47 T1 and 122 T2**, including **101 native TCIA masks: 25 T1 and 76 T2**. These are visual acquisition-identity decisions, not claims of identical voxel arrays or completed anatomical mask QC.
- **57** shared subjects have another MC-RC acquisition. **VS-SEG-126 has only its duplicated T1 acquisition.**
- London source aliases: **105/105** source scans from the 2022 package, and **79/79** from 2023, match the TCIA reference images exactly after canonical axis reorientation.
- Tilburg source aliases: **105/105** source scans match across 2022/2023; IDs are shuffled.
- UKM source aliases: **43/43** match MC-RC, comprising 40 exact full-voxel matches and three visual confirmations.
- UKM's 43 acquisitions include **19 already having TCIA native T1 masks** and **24 that gain a public T1 annotation through crossMoDA**. All 24 have same-study T2 scans with public masks.
- MC-RC/UKM T1 union: **88 acquisitions / 67 subjects**.
- London + Tilburg + original MC-RC/UKM: **420 T1 acquisitions before eligibility and segmentation QC**.
- Bilateral cochlea releases: **253 annotation records on 250 acquisitions**; UKM21/London126, UKM24/London095, and UKM27/London221 repeat acquisitions.
- MC-RC2 and UCSD were not included in the fingerprint archive. The expanded reported candidate pool is conditional on their release counts and local checks.

## Definitions and evidence

### Official versus derived duplicate relationships

- official_tcia_overlap_mapping preserves membership in TCIA's original eight-series table.
- same_acquisition_as_london_identified identifies confirmed acquisition overlap. The evidence field distinguishes official mapping from visual confirmation.
- duplicate_confirmed_by_image_matching_and_visual_review records the seven additional T1 relationships, not a claim that TCIA has already amended its table.
- duplicate_confirmed_by_visual_review records the three October 20 additions.
- different_acquisition_confirmed_by_visual_review records the 169 comparisons judged to be different acquisitions. This review covers the shared-subject subset, not every public scan.
- The historical filename exact_duplicate_series refers to the same acquisition, not byte-identical files or voxel arrays. Different defacing or slice coverage can change voxels.

### Public annotation availability

- Native TCIA mask fields describe the final repaired TCIA product only.
- public_t1_vs_annotation_available in the 124-row inventory includes either a native TCIA T1 annotation or a matched UKM source annotation.
- UKM VS subregions and cochlea share a multiclass label product. Whole-VS extraction requires the documented tumor-class union; cochlea must remain separate.
- A matched acquisition is not a completed mask transfer. Each annotation should remain paired with its release's reference image until geometry and labels are validated.
- same_study_t1_t2 and same-study T2 series keys use the MC-RC Study Instance UID, not merely matching calendar dates.
- Modalities counted within with_masks/without_masks folders do not describe all modalities acquired for the subject or examination.

### Matching methods

The source fingerprint audit analyzed 803 selected T1 images without reading errors. Complete scaled canonical float64 voxel arrays were hashed after axis flips/permutations, without resampling. Candidate patches comprised nonoverlapping non-flat central regions.

The initial 14 London–MC T1 pairs share 27/27 sampled central patches. Seven are supported by the official mapping; seven were visually confirmed on October 16 as defacing variants. The fifteenth T1 pair, VS-SEG-221, was confirmed visually on October 20 despite different axial slice coverage; no 27-patch or affine-equivalence result is inferred for that pair.

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

## Completed duplication review and mask preference

The 172-row completed review preserves each QC result and note from the maintainer's supplied table. Absolute workstation paths were removed; relative image/annotation paths, archive dates, series keys, and Study/Series Instance UIDs are retained. Dates are normalized to ISO format. Original evidence remains in previous_identity_evidence; manual_identity_qc_date denotes this review.

The maintainer often found MC-RC masks larger and better delineated than their London counterparts. Future curation provisionally favors the larger annotation when overlay review supports its anatomical quality and intended whole-VS definition. Compare physical volume in mm3 across grids; foreground voxel counts alone are not comparable. Larger size does not establish boundary accuracy. This update does not choose, alter, or transfer masks, and both released annotations should retain provenance.

## London surgical-status table

The [official crossMoDA 2022 source metadata](https://zenodo.org/records/6504722/files/infos_source_training.csv?download=1) explicitly marks 28 of the 105 London source scans as post-operative-london. The other 77 have numeric Koos grades; those grades are not independent confirmation of preoperative status. The remaining 137 London reference scans lie outside this source subset. No complete 242-scan surgical/fat-packing tally was verified.

london_surgical_status.csv joins these source records through the image-confirmed London crosswalk. source_surgical_status preserves the organizer evidence; resection_status_qc, fat_graft_visible_qc, qc_evidence, qc_confidence, qc_notes, and qc_date are blank for subsequent review. Suggested resection values: pre_resection, post_resection, indeterminate. Suggested visible-fat values: yes, no, indeterminate. A blank means not reviewed. Record status per scan/timepoint, not globally per subject.

Three scans explicitly marked postoperative in 2022 are retained under matched 2023 aliases: TCIA007 (2021ldn65/2023ldn57), TCIA080 (2021ldn28/2023ldn12), and TCIA246 (2021ldn23/2023ldn55). Conversely TCIA228/2021ldn15 has Koos4 but is absent from the 2023 source subset. These conflicts are flagged rather than resolved from challenge membership. No fat-graft status is inferred.

VS-SEG-131 is flagged as having no visible VS, confirmed by the maintainer and consistent with Mehta's exclusion. Its surgical status remains undetermined; the aggregate 49-versus-48 difference does not establish that this was the excluded postoperative scan. Prior radiosurgery alone is not prior microsurgical resection.

For image QC, a fat graft is intrinsically bright on non-fat-suppressed T1 and loses signal with fat suppression. When no graft is visible, look for an operative route, craniotomy defect, altered IAC or mastoid anatomy, resection cavity, and adjacent gliosis. A cropped scan may not resolve surgical status. Use post_resection with fat_graft_visible=no for postoperative scans without visible fat; this does not prove that fat was never used. [Postoperative imaging review](https://pubs.rsna.org/doi/full/10.1148/rg.297095713)

Linear IAC enhancement may reflect postoperative change. Serial imaging and clinical history help distinguish scar from residual tumor; enhancement alone does not settle the surgical-status label. [Longitudinal postoperative MRI study](https://pubmed.ncbi.nlm.nih.gov/12616190/)

## Sources and provenance

1. TCIA's series_overlap_between_VS-MC-RC_and_-VS-SEG.csv supplied the original eight acquisition correspondences.
2. The released Vestibular-Schwannoma-MC-RC_NIfTI-segmentation-info3.csv and conversion inventory supplied MRI metadata and public study/series UIDs.
3. The final repaired pair-validation inventory established the 301 native TCIA masks. Earlier rejection statuses were not used as final mask availability.
4. public_t1_identity_audit_20261015_152439.zip supplied image fingerprints, relative paths, and geometry across TCIA London, TCIA MC-RC, and the 2022/2023 source releases.
5. Targeted visual review on October 16, 2026 confirmed seven additional London–MC pairs and UKM2/6/35 as defacing variants.
6. The completed qc_duplication_review.csv supplied on October 20, 2026 established three further duplicates and 169 different acquisitions in the remaining shared-subject subset. Its SHA-256 is recorded in the summary JSON.
7. Official crossMoDA 2022 infos_source_training.csv supplies the partial surgical-status flags. Retrieved October 20, 2026; SHA-256: 694405a6ffbc1f0cfd82c49d74a4d5ddc9c5c4c44280eab77cc0ddef230c8ee4. The challenge release is licensed CC BY-NC-SA 4.0; this metadata join is a derived reference.

The ambiguous MC inventory links in the original fingerprint CSV were recovered uniquely by matching the SHA-256-derived series key to the original Series Instance UID. All 124 T1 metadata joins and final native-mask statuses reconciled.

Official sources: [London TCIA](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/), [MC-RC TCIA](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/), [official overlap explanation](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=157287455), [crossMoDA 2022](https://zenodo.org/records/6504722), [crossMoDA 2023](https://www.synapse.org/Synapse:syn51236108).

Cite the actual source dataset releases and identify these files as derived acquisition/availability summaries. Licenses differ between TCIA and challenge products; image identity does not replace either release's terms.
