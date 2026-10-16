# MC-RC / London overlap tables

**Inventory checked: October 15, 2026.**

These tables distinguish shared subjects from duplicated MRI series. They cover MC-RC scans whose subject identifiers begin with VS-SEG-, linking those subjects to the London TCIA collection.

| File | Rows | One row represents |
|---|---:|---|
| [mc_rc_l_sc_gk_subject_overlap.csv](mc_rc_l_sc_gk_subject_overlap.csv) | 58 | A shared subject and counts by modality |
| [mc_rc_l_sc_gk_series_overlap.csv](mc_rc_l_sc_gk_series_overlap.csv) | 187 | An MC-RC MRI series from a shared subject |
| [mc_rc_l_sc_gk_exact_duplicate_series.csv](mc_rc_l_sc_gk_exact_duplicate_series.csv) | 8 | An officially mapped duplicated series |

## Definitions

- exact_duplicate_per_official_TCIA_mapping means the MC-RC Series Instance UID is in TCIA's official eight-series overlap table. The corresponding London Series Instance UID is included.
- additional_not_listed_as_duplicate means the series is absent from that official table. It has not independently been established as unique through voxel-level matching.
- public_native_vs_mask_available records whether the audited public download contains a VS mask on that series' native grid. False does not rule out a public annotation on the paired modality's grid, a separately released challenge annotation, or a private annotation.
- Subject-level additional mask counts concern the corresponding additional series, not all scans from that subject.
- released_study_date and released_series_date are retained separately. Dates can be deidentified; they are not independently verified clinical calendar dates.
- Study and Series Instance UIDs refer to the MC-RC release unless the field explicitly begins with l_sc_gk.

## Reconciliation

The 58 shared subjects contribute 187 MC-RC scans: 62 T1 and 125 T2. Eight scans are officially mapped duplicates (seven T1, one T2); the remaining 179 are additional series (55 T1, 124 T2). All 58 subjects have at least one additional series.

Of those additional series, 33 T1 and 77 T2 have public native-grid VS masks in the audited download. For the 64 native-labeled MC-RC T1 scans overall, 40 belong to shared London subjects: seven duplicates and 33 additional scans. The other 24 belong to MC-RC-only identifiers.

## Sources and method

1. TCIA's official series_overlap_between_VS-MC-RC_and_-VS-SEG.csv establishes duplicated-series correspondence.
2. The released Vestibular-Schwannoma-MC-RC_NIfTI-segmentation-info3.csv supplies series metadata.
3. The complete conversion inventory supplies study/series UIDs and released study dates.
4. The final image-mask validation inventory confirms which 301 masks were actually present after geometry repair. Earlier mask-rejection statuses were not treated as final availability.

Metadata and inventories were joined by Series Instance UID; the final validation's series folders were checked against SHA256-derived UID identifiers. All 487 scans and 301 final masks reconciled. The CSVs contain no workstation paths or direct personal identifiers.

Official sources: [TCIA collection and downloadable mapping](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/), [TCIA overlap explanation](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=157287455).

TCIA distributes the underlying collection and overlap mapping under CC BY 4.0. Cite the [MC-RC dataset DOI](https://doi.org/10.7937/hrzh-2n82) and identify these as derived inventory summaries when reusing them.
