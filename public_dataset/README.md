# Public Vestibular Schwannoma MRI Datasets and crossMoDA

**Last checked: October 15, 2026**

A reference to the clinical cohorts, public scans and annotations, crossMoDA releases, and Kujawa's model-development cohorts. Section 2 contains the detailed cohort descriptions. Counts describe release availability, not a completed visual review of every scan or mask.

## Contents

1. [Terminology and annotation availability](#1-terminology-and-annotation-availability)
2. [Where the cohorts came from](#2-where-the-cohorts-came-from)
3. [Public T1 annotations at a glance](#3-public-t1-annotations-at-a-glance)
4. [crossMoDA editions, splits, and evaluation](#4-crossmoda-editions-splits-and-evaluation)
5. [Downloads, licenses, and citations](#5-downloads-licenses-and-citations)
6. [Identifiers and cross-release traceability](#6-identifiers-and-cross-release-traceability)
7. [How Kujawa et al. used the datasets](#7-how-kujawa-et-al-used-the-datasets)
8. [Sources](#8-sources)

## 1. Terminology and annotation availability

### 1.1 What each count means

| Term | Meaning in this README |
|---|---|
| **Subject** | One individual; longitudinal examinations do not create additional subjects. |
| **Examination / study / time point** | An imaging visit, potentially containing several MRI series. A Study Instance UID identifies a DICOM study. |
| **MRI series / scan** | One selected 3D MRI acquisition. Here, a reconstructed NIfTI scan represents one selected MRI series. |
| **DICOM instance** | An individual DICOM object, often one MRI slice; not one complete scan. |
| **Annotation / mask** | A segmentation associated with a reference scan and anatomy. One multiclass file can contain several anatomies. |
| **T1** | T1-weighted MRI; contrast administration must be established separately. |
| **ceT1 / T1CE / T1C** | Contrast-enhanced T1-weighted MRI. |
| **hrT2** | High-resolution T2-weighted MRI. |
| **VS** | Vestibular schwannoma. |
| **L-SC-GK / T-SC-GK** | London / Tilburg single-center Gamma Knife cohorts. |
| **MC-RC** | Multi-center routine clinical collection; use this name rather than MC-GK. |

Archive totals can include RTSTRUCT, RTPLAN, RTDOSE, and segmentation objects. Consequently, an archive's total series/object count need not equal its number of MRI scans.

### 1.2 "Publicly unannotated" versus challenge labels withheld

**Publicly unannotated means that no publicly released segmentation for the specified anatomy and reference scan has been verified.** It does not mean that no private annotation exists.

Always specify the anatomy and reference grid. A scan can have a VS annotation but no cochlea annotation. In a paired T1/T2 examination, a public T2-grid VS mask makes the examination annotated even when no separate T1-grid mask is supplied.

Keep these situations distinct:

- **Public scan with public annotation:** both can be downloaded.
- **Public scan without a verified public annotation:** the scan is publicly unannotated for the specified anatomy/grid.
- **Labels withheld in a challenge package:** participants receive no labels in that package; another archive can still publish annotations for the same underlying scan.
- **Private test scan:** the image itself is not part of the documented public release. Count it separately from publicly downloadable scans lacking masks.

In particular, London's challenge-target T2 scans should not be described as globally unannotated: TCIA independently provides clinical contours for the original London cohort.

### 1.3 Drawing modality, coordinate frame, and mask grid

These are separate provenance fields:

| Field | Question |
|---|---|
| Original drawing modality | Which images informed the delineation? |
| Contour coordinate frame | In which image's physical coordinates are the contour points expressed? |
| Mask reference grid | Which image supplies the mask's shape, spacing, orientation, and affine? |

London's T1 and T2 JSON files contain clinical contours mapped into their respective coordinate frames. A T2-space VS contour is therefore not evidence of an independently drawn T2 annotation. [TCIA contour documentation](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/)

### 1.4 TCIA clinical annotations versus crossMoDA annotations

- **London TCIA:** clinical tumor/target contours and, where present, cochlea contours. Cochlea coverage generally concerns the treated side.
- **crossMoDA 2021/2022:** whole VS and **bilateral cochlea** annotations in the labeled source release.
- **crossMoDA 2023:** intra-meatal VS, extra-meatal VS, and cochlea annotations. A whole-VS mask requires combining the VS subregions according to that release's label dictionary.

A bilateral-cochlea annotation record means coverage of that anatomy on one reference scan; it does not mean two separate NIfTI files. Counts below are anatomy-specific reference-scan records unless stated otherwise. [2021 annotation protocol](https://arxiv.org/html/2201.02831#S3.SS2.SSS3), [2023 task](https://crossmoda-challenge.ml/#task)

### 1.5 Availability is not a visual QC result

A nonempty mask does not by itself confirm the diagnosis, contour quality, complete coverage, or contrast administration. Final eligibility and case-level QC remain separate from the release inventories below.

For example, Mehta's external London review reported two non-contrast scans among 241 evaluated T1 scans and applied a study-specific exclusion. Those findings require reconciliation with scan identity and direct image review before being applied to another analysis. [Mehta et al., supplement](https://doi.org/10.3174/ajnr.A9112)

## 2. Where the cohorts came from

### 2.1 London: original public cohort and expanded challenge cohort

**Official TCIA collection:** Vestibular-Schwannoma-SEG  
**Clinical origin:** Queen Square Radiosurgery Centre, London, UK; Gamma Knife planning MRI.  
**Acquisition:** Siemens Avanto 1.5T; T1 MPRAGE and high-resolution T2.

#### Original public TCIA release

| Item | Count |
|---|---:|
| Subjects | 242 |
| Examinations | 242 |
| T1 scans | 242 |
| T2 scans | 242 |
| MRI series / scans | 484 |

The release includes DICOM MRI and radiotherapy objects, JSON contours in both modality coordinate frames, and T1/T2 registration transforms. The 484 MRI scans should not be confused with the archive's larger count of all DICOM series. [TCIA London collection](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/)

**Public segmentation coverage**

| Anatomy | T1 reference scans | T2 reference scans | Interpretation |
|---|---:|---:|---|
| Tumor/target contours in the VS release | 242 | 242 | Clinical annotations represented in both coordinate frames; final VS eligibility still requires QC. |
| Cochlea-named contours in the audited inventory | 146 | 146 | Coverage of 146 subjects; generally unilateral clinical annotations. |
| Scans lacking cochlea-named contours | 96 | 96 | Publicly unannotated for cochlea in this clinical release. |

The cochlea count is a **release-inventory observation**, not a statistic supplied by TCIA: 145 subjects have the exact name Cochlea, and one additional subject has alternate cochlea names. Separate modiolus labels are not counted as complete cochlea annotations. Multiple contours and mapped T1/T2 representations must not be counted as independent subjects or independently drawn masks.

Clinical annotation practice usually favored T1 for the tumor and T2 for the cochlea, while registered images could inform delineation. [Original London dataset paper](https://doi.org/10.1038/s41597-021-01064-w)

#### The London crossMoDA release adds a different cochlea annotation product

The labeled source subset contains **105 T1 scans with VS and bilateral-cochlea annotations**. These are source scans from the original 242-subject cohort, not 105 additional subjects.

The bilateral challenge annotations and the clinical TCIA cochlea contours are different annotation products. Do not add their counts to estimate unique scans with cochlea labels. The exact TCIA-to-crossMoDA subject crosswalk remains to be verified.

The 2023 London source subset contains 79 T1 scans after edition-specific exclusions; it is not a new independent London cohort. [Challenge split table](https://arxiv.org/html/2506.12006v4#S2.T1)

#### Why 242 and 379 both appear

| London group | Acquisition period reported by the challenge paper | Designated challenge role |
|---|---|---|
| Original 242-subject public cohort | October 2012-December 2017 | 105 labeled source T1, 105 target-training T2, 32 validation T2 |
| Additional 137-subject extension | January 2018-March 2021 | Private T2 testing |

Thus, **242 + 137 = 379 subjects** in the expanded 2021/2022 London challenge cohort. The designated challenge scans are one selected modality per subject; the original TCIA release separately contains both modalities.

Both modalities were acquired in the underlying clinical cohort. The additional 137 T2 test scans and their reference annotations were private in the documented challenge workflow; no public image/manual-label release for that extension was verified here. A complete 242-subject TCIA download is therefore complete for the original collection. [Original challenge paper, section 3.2.1](https://arxiv.org/html/2201.02831#S3.SS2.SSS1)

### 2.2 Tilburg: T-SC-GK

**Clinical origin:** Elisabeth-TweeSteden Hospital, Tilburg, Netherlands; Gamma Knife planning MRI.  
**Acquisition:** Philips Ingenia 1.5T; ceT1 3D-FFE and high-resolution T2 3D-TSE.  
**Challenge editions:** introduced in 2022 and retained in 2023.

The **376 designated challenge scans represent 376 subjects**, partitioned by their released/evaluated modality. They are not 376 publicly labeled T1 scans.

| Tilburg partition | Scans | Image availability | Public annotation availability |
|---|---:|---|---|
| Source training | 105 T1 | Public | VS and bilateral cochlea on the T1 reference scans |
| Target training | 105 T2 | Public | Labels withheld; no public T2 reference-mask release verified |
| Target validation | 32 T2 | Public | Labels withheld; organizer scoring |
| Target testing | 134 T2 | Private in the documented workflow | Organizer-held reference masks |
| **Total** | **376** | **242 public images + 134 private test images** | **105 public labeled T1 source scans** |

For the public source release, anatomy-specific coverage is **105 VS annotations and 105 bilateral-cochlea annotations**. The 2023 files subdivide VS into intra-/extra-meatal regions; the earlier release supplies whole VS.

Accordingly, **137 publicly downloadable T2 scans lack verified public VS/cochlea labels**. The separate 134 private test images should not be included in that public-image count. Label withholding does not establish that private annotations were never made.

There is no Tilburg TCIA collection identified in this reference; the verified public source annotations come from crossMoDA. The same 105-source-scan contribution appears in 2022 and 2023 with different release identifiers; match acquisitions before combining editions. [Official 2022 release](https://zenodo.org/records/6504722), [2023 release](https://www.synapse.org/Synapse:syn51236108), [challenge overview](https://doi.org/10.1016/j.media.2026.104282)

### 2.3 UK multi-center routine clinical cohort: MC-RC

**Official TCIA collection:** Vestibular-Schwannoma-MC-RC.

Routine scans were assembled through the London NHNN skull-base clinic from **10 UK medical sites, including London's L-SC-GK acquisition site and nine other sites**. The 58 shared London subjects are described below; that subject overlap is not a center-by-center enrollment breakdown. [Cohort origin, section 2.2.1](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

#### Collection composition and release history

| Item | Count |
|---|---:|
| Subjects | 160 |
| Examinations / time points | 427 |
| T1 MRI series / scans | 124 |
| T2 MRI series / scans | 363 |
| Total MRI series / scans | 487 |

Up to three selected examinations per subject capture longitudinal routine imaging.

The original partial release contained 124 subjects, 301 examinations, and 354 scans. **Version 2, updated June 4, 2026, added 133 series from 126 examinations**, making all 487 selected MRI scans available. This image-release update does not establish release of every corresponding annotation. [Current TCIA release history](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/)

#### Which VS annotations are publicly available?

The audited release contains **301 native-grid binary VS masks: 64 on T1 and 237 on T2**. There is no cochlea annotation product in the audited TCIA segmentation package.

| Examination type | Examinations | Scans | Examinations with a public VS annotation | Examinations without a public VS annotation |
|---|---:|---:|---:|---:|
| T1 only | 64 | 64 T1 | 64 | 0 |
| T2 only | 303 | 303 T2 | 184 | 119 |
| Paired T1 and T2 | 60 | 60 T1 + 60 T2 | 53, with a T2-grid mask | 7 |
| **Total** | **427** | **487** | **301** | **126** |

For the 53 annotated paired examinations, both scans are public and the reference mask is on T2. A second native T1-grid mask is not supplied. The other seven paired examinations have neither mask.

| Reference scans | Public native-grid VS masks | Scans without their own native-grid VS mask |
|---|---:|---:|
| T1: 124 | 64 | 60 |
| T2: 363 | 237 | 126 |
| **All: 487** | **301** | **186** |

These are two different denominators:

- **126 publicly unannotated examinations:** 119 T2-only plus seven paired examinations.
- **186 scans lacking their own native-grid mask:** 119 T2-only scans, 53 T1 scans whose paired T2 has a mask, and 14 scans from the seven unannotated paired examinations.

Paired examinations were annotated on the higher-resolution grid with the other modality also inspected. Thus, "T2-grid annotation" does not mean T1 was ignored during delineation. [Ground-truth protocol, section 2.2.7](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

Availability counts are the October 2026 inventory of the downloaded release, not a claim that private annotations do not exist. The public [overlap data and provenance](data/README.md) record how the inventory was reconciled.

#### Shared subjects and true series overlap with London

**58 subjects occur in both MC-RC and L-SC-GK. Only eight MRI series are officially listed as duplicated acquisitions: seven T1 and one T2.** The official mapping links their differing Series Instance UIDs across collections. Different exports and defacing can change metadata and facial pixels. [TCIA overlap documentation](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=157287455)

Within the MC-RC scans belonging to those 58 shared subjects:

| Category | T1 scans | T2 scans | Total scans |
|---|---:|---:|---:|
| All scans from shared subjects | 62 | 125 | 187 |
| Officially listed duplicated series | 7 | 1 | 8 |
| Additional series, not listed as duplicates | 55 | 124 | 179 |
| Additional series with public native-grid VS masks | 33 | 77 | 110 |

**All 58 shared subjects contribute at least one additional MC-RC series.** Removing every shared subject would discard distinct follow-up scans.

For the 64 native-labeled MC-RC T1 scans specifically: 40 belong to shared London subjects, consisting of seven duplicated acquisitions and **33 additional scans**. The other 24 belong to MC-RC-only subject identifiers.

| Shared subject | Released MC-RC study date | Duplicated modality |
|---|---|---|
| VS-SEG-095 | 1996-11-16 | T1 |
| VS-SEG-111 | 1997-03-23 | T1 |
| VS-SEG-117 | 1996-08-15 | T1 |
| VS-SEG-133 | 1997-04-24 | T2 |
| VS-SEG-135 | 1997-02-23 | T1 |
| VS-SEG-154 | 1997-10-10 | T1 |
| VS-SEG-188 | 1997-11-19 | T1 |
| VS-SEG-199 | 1998-02-02 | T1 |

The T2 duplication for subject 133 does not make that subject's London T1 a duplicated T1 acquisition.

Download the supporting tables:

- [58 shared subjects](data/mc_rc_l_sc_gk_subject_overlap.csv): counts of duplicated and additional scans, by modality and public mask availability.
- [187 series from shared subjects](data/mc_rc_l_sc_gk_series_overlap.csv): dates, study/series UIDs, mask availability, and official overlap status.
- [Eight exact duplicate series](data/mc_rc_l_sc_gk_exact_duplicate_series.csv): both collections' Series Instance UIDs.

Here, "additional" means not listed as duplicated in TCIA's official eight-series mapping. It is not a claim that this repository has completed independent voxel-level identity matching. Released dates can be deidentified; study and series dates are retained separately.

#### The related UKM crossMoDA 2023 annotation release

crossMoDA 2023 supplies **43 labeled source T1 scans from 38 subjects**, with VS subregions and bilateral-cochlea annotations created for that challenge. These annotations are distinct from the original TCIA VS-only product.

Their exact correspondence to the 64 native-labeled TCIA T1 scans has not been established. Some could correspond to paired-examination T1 scans that lack a native T1 mask in TCIA. Do not assume all 43 are already counted, or that all 43 are additional acquisitions. [Challenge annotation description and Table 1](https://arxiv.org/html/2506.12006v4)

### 2.4 MC-RC2: a separate, newer collection

**MC-RC2 is not Version 2 of MC-RC.**

The separate TCIA collection contains **190 subjects, 621 examinations, and 1,157 scans: 543 T1CE, 481 T1, and 133 T2**. It originated through King's College Hospital from more than 15 hospitals in Southeast England. The authors report no overlap with their previous datasets.

Public binary VS masks accompany **534 T1CE scans from 184 subjects**. Nine postoperative T1CE scans have no visible residual tumor and no mask file. Thus, 623 scans lack their own described VS-mask file: those nine plus 481 T1 and 133 T2 scans. No cochlea annotation release is described.

The annotations use model initialization followed by expert review and correction. The release is already NIfTI; it has not undergone this repository's file-level audit. [TCIA MC-RC2](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc2/), [2026 dataset paper](https://doi.org/10.1038/s41597-026-08211-1)

### 2.5 UCSD-VS-Longitudinal: another public T1 reference set

This separate collection contains **191 subjects and 570 examinations**. Each examination includes a post-contrast T1 scan and a binary VS reference segmentation; dedicated post-contrast IAC imaging supplies the reference when available. Nearly all examinations also include pre-contrast T1 and T2.

The initial masks came from a model trained on London data, followed by manual correction and neuroradiologist approval. This annotation-model provenance does not make the UCSD scans London acquisitions. No cochlea label release is described.

TCIA reports 570 annotated T1 reference examinations; its larger combined image/segmentation object count should not be read as an MRI-only scan count. Additional T1/T2 series should not automatically be treated as separately annotated reference scans. Their publicly unannotated scan count has not been established from a file inventory. The release has not been locally audited. [UCSD collection and reference-scan rules](https://www.cancerimagingarchive.net/collection/ucsd-vs-longitudinal/)

## 3. Public T1 annotations at a glance

| Public reference set | T1 VS annotation records | T1 cochlea annotation records | Counting caveat |
|---|---:|---:|---|
| London TCIA | 242 tumor/target contour sets | 146 subjects with cochlea-named contours | Clinical release; VS eligibility pending QC; cochlea generally unilateral |
| London crossMoDA 2021/2022 source | 105 | 105 bilateral | A subset of the London TCIA cohort |
| Tilburg crossMoDA 2022/2023 source | 105 | 105 bilateral | Repeated editions must not be added |
| MC-RC TCIA, native T1 grid | 64 | 0 in this product | Contains seven duplicated London T1 acquisitions |
| UKM crossMoDA 2023 source | 43 | 43 bilateral | TCIA correspondence unresolved |
| MC-RC2 | 534 | No release described | Separate collection; not locally audited |
| UCSD-VS-Longitudinal | 570 reference examinations | No release described | Reference-scan and file counts not locally audited |

The historical three-component inventory yields **242 + 105 + 64 - 7 = 404 candidate T1 acquisitions before visual QC**, when retaining the MC-RC copy of each duplicated London T1. That is **not a complete total of currently public T1 data**: UKM alias matching remains unresolved, and MC-RC2 and UCSD are outside that inventory.

For bilateral cochlea annotations, the London, Tilburg, and UKM source releases provide **105 + 105 + 43 = 253 annotation records before cross-release matching**. Their unique-acquisition count is not yet established. Original unilateral TCIA cochlea contours do not supply equivalent bilateral coverage.

## 4. crossMoDA editions, splits, and evaluation

### 4.1 Designated challenge scans

Each cell below counts the scan selected for that benchmark role, not all modalities acquired clinically.

| Edition | Cohort | Labeled T1 source | T2 target training | T2 validation | Private T2 testing | Total |
|---|---|---:|---:|---:|---:|---:|
| 2021 | London | 105 | 105 | 32 | 137 | 379 |
| 2022 | London | 105 | 105 | 32 | 137 | 379 |
| 2022 | Tilburg | 105 | 105 | 32 | 134 | 376 |
| 2023 | London | 79 | 85 | 32 | 113 | 309 |
| 2023 | Tilburg | 105 | 105 | 32 | 134 | 376 |
| 2023 | UK MC-RC | 43 | 105 | 32 | 94 | 274 |

The 2023 UK contribution contains 274 scans from 145 subjects, including longitudinal scans. The editions overlap; their totals must not be added as distinct subjects. Postoperative exclusions changed the 2023 subsets. [Organizers' Table 1](https://arxiv.org/html/2506.12006v4#S2.T1)

### 4.2 Source, target training, validation, and testing

| Role | Participant access | Purpose |
|---|---|---|
| Source training | T1 scans and labels | Supervised source segmentation |
| Target training | T2 scans without supplied labels | Unsupervised adaptation |
| Target validation | T2 scans; labels hidden | Quantitative leaderboard feedback |
| Target testing | Submitted algorithm runs on private scans | Final organizer-controlled evaluation |

Source and target training scans were supplied as **unpaired groups**, not matching T1/T2 examinations. For London 2021, source, target-training, and validation groups comprised different subjects. [Original partition](https://arxiv.org/html/2201.02831#S3.SS2.SSS1)

Validation predictions were scored against hidden annotations. Final testing used submitted Docker containers. Hidden labels therefore supported numerical evaluation, rather than visual inspection alone. [Official evaluation instructions](https://crossmoda2022.grand-challenge.org/instructions-for-submission/)

### 4.3 Challenge permissions versus independent archive availability

The challenge prohibited additional data/annotations, including the separate TCIA release. A contour's independent public availability did not make it permitted challenge supervision. [Official rules](https://crossmoda-challenge.ml/challenge2022/)

For London, labels withheld in the challenge can coexist with public clinical annotations in TCIA. For Tilburg, no corresponding public T2 annotation release was verified. For UKM, challenge-to-TCIA identity and annotation matching remain unresolved. A competition ending does not itself establish release of private scans or labels.

## 5. Downloads, licenses, and citations

| Release | Official download | Contents | Reported data license |
|---|---|---|---|
| London TCIA | [Vestibular-Schwannoma-SEG](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/) | DICOM MRI/RT objects; JSON contours and transforms | CC BY 4.0 |
| MC-RC TCIA | [Vestibular-Schwannoma-MC-RC](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/) | DICOM scans; NIfTI VS masks; overlap mapping | CC BY 4.0 |
| MC-RC2 | [Vestibular-Schwannoma-MC-RC2](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc2/) | NIfTI scans/masks and clinical metadata | CC BY 4.0 |
| UCSD | [UCSD-VS-Longitudinal](https://www.cancerimagingarchive.net/collection/ucsd-vs-longitudinal/) | NIfTI scans/masks and clinical metadata | CC BY 4.0 |
| crossMoDA 2021 | [Zenodo 4662239](https://zenodo.org/records/4662239) | Training and validation archives | CC BY 4.0, as documented in the 2021 paper |
| crossMoDA 2022 | [Zenodo 6504722](https://zenodo.org/records/6504722) | Training/validation archives and source metadata | CC BY-NC-SA 4.0 |
| crossMoDA 2023 | [Synapse syn51236108](https://www.synapse.org/Synapse:syn51236108) | Challenge releases; account/access requirements apply | CC BY-NC-SA 4.0 |

Use TCIA's Data Access section for the current files and download mechanism. DICOM collections use TCIA Data Retriever; supplementary NIfTI/metadata packages are separate downloads. Synapse access must be checked at the file level.

Cite the **dataset DOI and release version actually used**, together with the relevant methods/challenge paper. The collection pages provide their required data citations. A paper's copyright license does not establish its dataset's license.

Verify the license attached to the downloaded package. In particular, do not replace the non-commercial/share-alike terms of a challenge release with the license of a related TCIA collection. License sources: collection pages above; [2021 data preparation](https://arxiv.org/html/2201.02831#S3.SS2.SSS4), [2022 release terms](https://zenodo.org/records/6504722), [2023 data curation](https://arxiv.org/html/2506.12006v4#S2.SS4.SSS1).

## 6. Identifiers and cross-release traceability

### 6.1 Preserve release aliases

| Source identifier | Meaning |
|---|---|
| TCIA VS-SEG-NNN | London subject identifier, also reused for shared MC-RC subjects |
| TCIA VS-MC-RC-NNN | MC-RC subject identifier outside the London cohort |
| crossmoda2021_ldn_* | London source identifiers retained inside the 2022 package |
| crossmoda2022_etz_0 through _104 | Tilburg 2022 source identifiers; numbering starts at zero |
| crossmoda2023_ldn_*, _etz_*, _ukm_* | Edition-specific 2023 identifiers |

No official TCIA-to-crossMoDA or 2022-to-2023 case crosswalk was verified. Numeric similarity, adding one, or padding identifiers does not establish identity. The 2022 source CSV contains challenge name, group, center, and Koos information rather than TCIA Series Instance UIDs. [2022 source metadata](https://zenodo.org/records/6504722/files/infos_source_training.csv?download=1)

### 6.2 Recommended canonical names

Use one acquisition ID for the image and its anatomy-specific masks, retaining every source-release name as an alias. For example:

~~~text
l_sc_gk_095_1996_11_16_T1_scan.nii.gz
l_sc_gk_095_1996_11_16_T1_vs.nii.gz
l_sc_gk_095_1996_11_16_T1_cochlea.nii.gz

mc_rc_085_1991_04_11_T1_scan.nii.gz
mc_rc_085_1991_04_11_T1_vs.nii.gz

crossmoda2022_etz_0_T1_scan.nii.gz
crossmoda2022_etz_0_T1_vs.nii.gz
crossmoda2022_etz_0_T1_cochlea.nii.gz
~~~

Here, l_sc_gk preserves the VS-SEG subject lineage even when a distinct examination is obtained from MC-RC. A manifest separately records the selected download collection. Use a released date when available; append a short series identifier only when subject/date/modality collide.

Keep T1 stable in filenames and record contrast status separately. Preserve original MC-RC2/UCSD names as aliases, including reference-scan selection. Released dates can be shifted and should not be assumed comparable across archives.

Do not apply a final rename until acquisition matching is resolved. Store subject ID, study/series UID, release/edition aliases, anatomy, annotation source, drawing-modality evidence, reference grid, contrast status, and QC status in the provenance manifest.

## 7. How Kujawa et al. used the datasets

### 7.1 Published experiment counts

| Input | MC-RC training | MC-RC testing | SC-GK training | SC-GK testing | Tilburg testing |
|---|---:|---:|---:|---:|---:|
| T1 | 52 | 12 | 196 | 46 | 105 |
| T2 | 291 | 72 | 196 | 46 | 32 |
| T1+T2 | 48 | 12 | 196 | 46 | Not available |

The reported MC-RC T1 split totals 64 cases, matching the T1-only examination count, rather than all 124 T1 scans. The paired split totals 60. Development/test partitions were subject-separated, with five-fold development cross-validation. [Kujawa, Table 2 and section 2.6](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

### 7.2 Combined models: published counts and prepared entries

| Input | Component training counts | Combined count printed in Table 2 | Released numTraining | Arithmetic reconstruction |
|---|---|---:|---:|---|
| T1 | 52 + 196 | 248 | 404 | 52 x 4 + 196 |
| T2 | 291 + 196 | 248 | 487 | 291 + 196 |
| T1+T2 | 48 + 196 | 248 | 388 | 48 x 4 + 196 |

Released metadata is under Dataset920_VSMCRCSCGKT1, Dataset921_VSMCRCSCGKT2, and Dataset922_VSMCRCSCGKT1T2. The descriptions mention repeated cases for balancing. [Official model archive](https://zenodo.org/records/10363647)

The totals support **four representations of each MC-RC T1/paired training case and no expansion for T2**. This is an arithmetic reconstruction; exact membership and repetition require case-level manifests. Table 2's combined T2/paired counts remain inconsistent with the component sums.

numTraining counts prepared entries, not unique subjects or acquisitions. A two-channel entry contains both scans. The additional 137 private London subjects are not needed to explain these totals. [nnU-Net integrity check](https://github.com/MIC-DKFZ/nnUNet/blob/master/nnunetv2/experiment_planning/verify_dataset_integrity.py)

### 7.3 Paired-input registration and ground truth

T1 was affine-registered/resampled onto the T2 reference grid. Images used cubic-spline interpolation; labels used nearest-neighbor interpolation. Paired MC-RC reference masks occupy T2 space. Using the existing SC-GK T2-space VS mask is likely, but the selected source file is not explicitly documented.

| Stage | Inputs | Ground-truth role |
|---|---|---|
| Training | T1 aligned to T2, plus T2 | Supervises the loss |
| Test inference | T1 aligned to T2, plus T2 | Not required |
| Test scoring | Predicted segmentation | Compared with the reference annotation |

The common preprocessing implies alignment of both training and test inputs. Resampling onto a finer grid adds no acquired detail. Subsequent nnU-Net target-spacing resampling is separate. [Kujawa, sections 2.5-2.6](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

### 7.4 External Tilburg evaluation and overlap

The external tests used Tilburg's 105 source T1 scans and 32 T2 validation scans. The paper gives no reason for excluding the other T2 partitions; their annotation/access status should not be inferred from that choice.

Kujawa was among the challenge organizers, whose documented access arrangement allowed access to private tests when needed. This does not establish which private files were used in this particular study. [Official 2022 release](https://zenodo.org/records/6504722)

Shared-series subjects were assigned to development partitions to avoid cross-collection train/test leakage. This does not establish removal of every duplicated combined-model entry. The actual shared scans and distinct follow-up acquisitions are documented in section 2.3.

## 8. Sources

### Cohorts and annotations

- **London TCIA:** [collection and required data citation](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/), DOI [10.7937/TCIA.9YTJ-5Q73](https://doi.org/10.7937/TCIA.9YTJ-5Q73).
- **Shapey et al., 2021:** original London dataset paper, [10.1038/s41597-021-01064-w](https://doi.org/10.1038/s41597-021-01064-w).
- **MC-RC TCIA:** [collection, release history, masks, and overlap mapping](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/), DOI [10.7937/hrzh-2n82](https://doi.org/10.7937/hrzh-2n82).
- **Kujawa et al., 2024:** comparative study and model methods, [full paper](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full).
- **MC-RC2:** [TCIA collection](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc2/), DOI [10.7937/BQ0Z-XA62](https://doi.org/10.7937/BQ0Z-XA62); Wijethilake et al., 2026, [dataset paper](https://doi.org/10.1038/s41597-026-08211-1).
- **UCSD-VS-Longitudinal:** [TCIA collection, reference-scan rules, and required citation](https://www.cancerimagingarchive.net/collection/ucsd-vs-longitudinal/).
- **Mehta et al., 2025:** external T1 evaluation and supplement, [10.3174/ajnr.A9112](https://doi.org/10.3174/ajnr.A9112).

### Challenges and released models

- **Dorent et al., crossMoDA 2021:** [published paper](https://doi.org/10.1016/j.media.2022.102628), [open manuscript](https://arxiv.org/html/2201.02831).
- **Wijethilake et al., 2026 challenge retrospective:** [published paper](https://doi.org/10.1016/j.media.2026.104282), [open manuscript and split table](https://arxiv.org/html/2506.12006v4).
- **Official releases:** [2021 Zenodo](https://zenodo.org/records/4662239), [2022 Zenodo](https://zenodo.org/records/6504722), [2023 Synapse](https://www.synapse.org/Synapse:syn51236108).
- **Official challenge website:** [crossmoda-challenge.ml](https://crossmoda-challenge.ml/).
- **Kujawa's released models:** [Zenodo 10363647](https://zenodo.org/records/10363647).
- **Original London preprocessing:** [KCL-BMEIS/VS_Seg](https://github.com/KCL-BMEIS/VS_Seg).
- **Repository overlap tables:** [data definitions and provenance](data/README.md).
