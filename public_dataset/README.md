# Vestibular Schwannoma MRI Datasets and crossMoDA: A Practical Reference

**Last checked: October 13, 2026**

This README documents the relationships between the public vestibular schwannoma datasets, their annotation releases, and the crossMoDA challenges. It also records the conventions used for this repository’s TCIA-to-NIfTI conversion.

> **The main distinction:** a clinical cohort, a public dataset release, and a challenge split can contain different subsets of the same patients. Their names and sample sizes are not interchangeable.

## Contents

- [1. Dataset names and terminology](#1-dataset-names-and-terminology)
- [2. Where the cohorts came from](#2-where-the-cohorts-came-from)
- [3. Why London has both 242 and 379 patients](#3-why-london-has-both-242-and-379-patients)
- [4. crossMoDA editions and sample sizes](#4-crossmoda-editions-and-sample-sizes)
- [5. Downloads and label availability](#5-downloads-and-label-availability)
- [6. Annotation differences](#6-annotation-differences)
- [7. How Kujawa et al. used the datasets](#7-how-kujawa-et-al-used-the-datasets)
- [8. Overlap and dataset splitting](#8-overlap-and-dataset-splitting)
- [9. This repository’s conversion policy](#9-this-repositorys-conversion-policy)
- [10. Findings from the converted inventory](#10-findings-from-the-converted-inventory)
- [11. Frequently confused points](#11-frequently-confused-points)
- [12. Sources](#12-sources)

## 1. Dataset names and terminology

| Term | Meaning |
|---|---|
| **VS** | Vestibular schwannoma |
| **ceT1 / ceT1w / T1C** | Contrast-enhanced T1-weighted MRI |
| **hrT2** | High-resolution T2-weighted MRI |
| **GK** | Gamma Knife |
| **SC-GK** | Single-center Gamma Knife dataset |
| **T-SC-GK** | Tilburg single-center Gamma Knife dataset |
| **MC-RC** | Multi-center routine clinical dataset |
| **TCIA** | The Cancer Imaging Archive |
| **crossMoDA** | Cross-Modality Domain Adaptation challenge |
| **Source training data** | Annotated ceT1 images used to learn segmentation |
| **Target training data** | T2 images provided without manual labels for domain adaptation |
| **Validation data** | Images used for challenge feedback; manual ground truth is withheld |
| **Test data** | Held-out challenge evaluation data |
| **Unpaired** | The released source and target training images are not supplied as matched T1/T2 examinations |
| **Foreground class** | A segmented structure; excludes background |

**Use `MC-RC`, not `MC-GK`, when referring to Kujawa’s multi-center routine clinical collection.** The cohort definitions appear in [Kujawa et al., §§2.2–2.4](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2).

## 2. Where the cohorts came from

### 2.1 London: original public TCIA collection

**Official collection:** `Vestibular-Schwannoma-SEG`

- **Origin:** Queen Square Radiosurgery Centre, London, UK.
- **Purpose:** Gamma Knife treatment-planning MRI.
- **Public cohort:** 242 patients.
- **MRI:** one T1 and one T2 examination per patient, giving 484 MRI volumes.
- **Scanner:** Siemens Avanto 1.5T.
- **Acquisition:** T1 MPRAGE and high-resolution T2 sequences.
- **Release:** MRI and radiotherapy objects in DICOM; supplementary JSON contours and ITK `.tfm` transforms.
- **Role:** the original London data underlying the public crossMoDA 2021 training/validation splits.

**Download:** [TCIA Vestibular-Schwannoma-SEG](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/).

**Processing code:** [KCL-BMEIS/VS_Seg](https://github.com/KCL-BMEIS/VS_Seg).

The collection’s Version 2 added the JSON contours and registration transforms. TCIA lists the release under **CC BY 4.0**. [TCIA collection description and Data Access](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/)

### 2.2 London: expanded challenge collection

The London collection used by crossMoDA 2021 included **379 patients**, incorporating the original public cohort plus a later private test cohort.

This expanded challenge collection is frequently called **London SC-GK**. Keep its release context attached to the name:

```text
London original public TCIA collection: 242 patients
London expanded crossMoDA 2021 collection: 379 patients
```

The expansion is documented in [Dorent et al., §3.2.1](https://arxiv.org/html/2201.02831#S3.SS2.SSS1).

### 2.3 Tilburg: separate Gamma Knife cohort

**Names:** `Tilburg SC-GK`, `T-SC-GK`

- **Origin:** Elisabeth-TweeSteden Hospital, Tilburg, Netherlands.
- **Purpose:** Gamma Knife treatment-planning MRI.
- **MRI:** ceT1 and high-resolution T2.
- **Scanner:** Philips Ingenia 1.5T.
- **Acquisition:** ceT1 3D-FFE and T2 3D-TSE.
- **Public challenge ceT1 training subset:** 105 scans.

Tilburg is a separate institution and cohort from London. Its acquisition details are described in [Kujawa et al., §2.4](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2).

It first appeared in **crossMoDA 2022**, and remained in the 2023 edition. The complete Tilburg contribution reported for those editions was **376 designated challenge scans**, including private testing data. [Challenge retrospective, Table 1](https://arxiv.org/html/2506.12006v1#S2.SS2.SSS1)

### 2.4 UK multi-center routine clinical collection

**Official collection:** `Vestibular-Schwannoma-MC-RC`

Unlike the London and Tilburg planning datasets, this collection contains longitudinal routine clinical examinations with varied acquisition protocols.

| Published collection measure | Count |
|---|---:|
| Patients | 160 |
| Examination time points | 427 |
| MRI volumes | 487 |
| ceT1 volumes | 124 |
| T2 volumes | 363 |

Data came from **10 UK medical sites**, with up to three selected time points per patient. [Kujawa et al., §§2.2.1–2.2.5](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

**Download:** [TCIA Vestibular-Schwannoma-MC-RC](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/).

**Important availability update:** TCIA Version 2, dated **June 4, 2026**, reports release of previously embargoed images: 133 series from 126 time points. The current collection lists all 160 patients, 427 studies, and 487 series, plus NIfTI segmentations and an overlap-mapping CSV. Older descriptions of a 124-patient partial release are therefore outdated. [TCIA Version 2 release notes](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/)

## 3. Why London has both 242 and 379 patients

The crossMoDA 2021 paper distinguishes:

| Patient group | Acquisition period reported by the challenge paper | Role |
|---|---|---|
| Original 242-patient TCIA collection | October 2012–December 2017 | Training and validation |
| Additional 137-patient collection | January 2018–March 2021 | Private testing |

The original public patients were partitioned as follows:

```text
105 patients → annotated ceT1 source training
105 patients → T2 target training, without released labels
 32 patients → T2 validation, without released labels
────────────────────────────────────────────────────────
242 original public-cohort patients

137 additional patients → private T2 challenge testing
────────────────────────────────────────────────────────
379 expanded London challenge patients
```

The increase reflects **additional patients**, not double-counting T1 and T2. The paper states that both modalities were acquired for the underlying patients, although the benchmark supplied only the designated modality for each group. [Dorent et al., §3.2.1 and Table 1](https://arxiv.org/html/2201.02831#S3.SS2.SSS1)

**A complete 242-patient TCIA download is not missing 137 patients.** Those patients belong to the separate challenge extension.

## 4. crossMoDA editions and sample sizes

The challenge progresses from annotated **ceT1 source images** to segmentation on **T2 target images**. Its official website describes the task and participating data sources. [crossMoDA website](https://crossmoda-challenge.ml/)

| Edition | Data sources | Tasks |
|---|---|---|
| **2021** | London | Whole VS and cochlea segmentation |
| **2022** | London + Tilburg | Whole VS/cochlea segmentation; additional Koos classification task |
| **2023** | London + Tilburg + UK MC-RC | Intra-meatal VS, extra-meatal VS, and cochlea segmentation |

The organizers’ report states that postoperative scans were excluded from the 2023 challenge; consequently, its subsets differ from earlier releases. [Challenge retrospective, §2.2.1](https://arxiv.org/html/2506.12006v1#S2.SS2.SSS1)

### Challenge split counts

The following counts describe **designated benchmark scans**, not every modality acquired for every patient.

| Edition | Cohort | Annotated ceT1 training | Unlabeled T2 training | T2 validation | Private T2 testing | Total |
|---|---|---:|---:|---:|---:|---:|
| 2021 | London | 105 | 105 | 32 | 137 | 379 |
| 2022 | London | 105 | 105 | 32 | 137 | 379 |
| 2022 | Tilburg | 105 | 105 | 32 | 134 | 376 |
| 2022 | **Combined** | **210** | **210** | **64** | **271** | **755** |
| 2023 | London | 79 | 85 | 32 | 113 | 309 |
| 2023 | Tilburg | 105 | 105 | 32 | 134 | 376 |
| 2023 | UK MC-RC | 43 | 105 | 32 | 94 | 274 |
| 2023 | **Combined** | **227** | **295** | **96** | **341** | **959** |

The 2023 UK MC-RC contribution comprises **274 scans from 145 patients**. Do not interpret the combined 959 scans as 959 unique patients. Source: [organizers’ Table 1](https://arxiv.org/html/2506.12006v1#S2.SS2.SSS1).

**Edition-specific cohorts overlap.** Do not add the 2021, 2022, and 2023 totals to estimate a unique dataset size.

## 5. Downloads and label availability

### Official download locations

| Release | Where to download | Format / contents |
|---|---|---|
| Original London TCIA | [Vestibular-Schwannoma-SEG](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/) | DICOM MRI/RT objects, JSON contours, `.tfm` transforms |
| UK routine clinical TCIA | [Vestibular-Schwannoma-MC-RC](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/) | DICOM images, NIfTI segmentation ZIP, overlap mapping |
| crossMoDA 2021 | [Zenodo record 4662239](https://zenodo.org/records/4662239) | Training and validation ZIPs |
| crossMoDA 2022 | [Zenodo record 6504722](https://zenodo.org/records/6504722) | Training/validation ZIPs, source metadata CSV, GIF parcellations |
| crossMoDA 2023 | [Synapse project syn51236108](https://www.synapse.org/Synapse:syn51236108) | Challenge data; check account and project access |

For TCIA DICOM downloads, use the collection’s Data Access section and TCIA Data Retriever. Supplementary ZIP files are listed separately.

For Synapse, check each file’s access status. A project being visible does not establish download permission for every file. [Synapse download documentation](https://docs.synapse.org/synapse-docs/finding-and-downloading-data)

### Downloadable images and downloadable ground truth are different

| Challenge component | Images | Manual segmentation labels |
|---|---|---|
| ceT1 source training | Released | Released |
| T2 target training | Released | Withheld in the challenge package |
| T2 validation | Released | Withheld; evaluated through the challenge |
| T2 testing | Private in the documented challenge workflow | Held by organizers |

The original TCIA release may independently provide labels for patients assigned to unlabeled challenge splits. That does not change the challenge’s permitted-data rules.

For the **137-patient London extension**, no official public test-image/manual-label archive was verified when this README was prepared. The 2021 Zenodo record lists only training and validation archives. [Official 2021 release](https://zenodo.org/records/4662239)

The later report also documents private test evaluation using submitted containers. Competition completion does not, by itself, establish a subsequent public release. [Challenge evaluation protocol](https://arxiv.org/html/2506.12006v1#S2.SS5)

**June 2026 distinction:** the MC-RC embargo release concerns the routine clinical parent collection. It does not establish release of the separate London 137-patient extension or of every challenge-specific label package.

### Release licenses

| Release | Reported license |
|---|---|
| London TCIA | CC BY 4.0 |
| MC-RC TCIA | CC BY 4.0 |
| crossMoDA 2021 training/validation | CC BY 4.0 |
| crossMoDA 2022 training/validation | CC BY-NC-SA 4.0 |
| crossMoDA 2023 training/validation | CC BY-NC-SA 4.0 |

Verify the license attached to the actual downloaded release. Sources: [London TCIA](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/), [MC-RC TCIA](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/), [2021 paper §3.2.4](https://arxiv.org/html/2201.02831#S3.SS2.SSS4), [2022 release](https://zenodo.org/records/6504722), and [2023 release protocol](https://arxiv.org/html/2506.12006v1#S2.SS4.SSS1).

## 6. Annotation differences

### 6.1 Original TCIA annotation modality versus coordinate space

In the London cohort, VS was usually drawn on ceT1 and refined using registered T2. Some tumors were primarily delineated on T2. Cochlea was typically delineated on T2. These are usual practices, not universal patient-level provenance rules. [Shapey et al., Methods](https://discovery.ucl.ac.uk/id/eprint/10137674/1/s41597-021-01064-w.pdf)

Both modality folders contain `contours.json`, with structures already expressed in their corresponding coordinate frames.

Therefore:

- A cochlea contour in a T1 folder does not establish that it was drawn on T1.
- A VS contour in a T2 folder does not establish an independent T2 annotation.
- A filename ending in `refT1` or `refT2` identifies the exported grid, not the original drawing modality.

GammaPlan’s RTSTRUCT exports contain interpolated slice-aligned contours. The JSON release preserves the original contours after coordinate mapping, allowing conversion of potentially off-slice contours with SlicerRT. [Shapey et al., Data Records](https://discovery.ucl.ac.uk/id/eprint/10137674/1/s41597-021-01064-w.pdf)

### 6.2 crossMoDA cochlea annotations

The crossMoDA annotation protocol added **bilateral cochlea annotations**, produced using T2 as reference. The original clinical planning contours generally focused on the cochlea nearest the tumor. [Dorent et al., §3.2.3](https://arxiv.org/html/2201.02831#S3.SS2.SSS3)

Consequently, the same patient’s original TCIA cochlea mask and challenge cochlea mask need not be identical.

### 6.3 crossMoDA 2023 labels

The 2023 task distinguishes **intra-meatal** and **extra-meatal** tumor regions, in addition to cochlea. A whole-tumor mask cannot be compared directly with only one of those subregions. Check each release’s label-value mapping before combining datasets. [Official 2023 task description](https://crossmoda-challenge.ml/#task)

Do not assume all releases use the same integer values for corresponding classes.

## 7. How Kujawa et al. used the datasets

### 7.1 Four different counts must be distinguished

| Count | What it measures | Example |
|---|---|---|
| Full collection size | All examinations in a released cohort | 124 MC-RC ceT1 volumes |
| Experimental training subset | Cases selected for a particular experiment | 52 MC-RC cases in the paper’s T1 experiment |
| Prepared nnU-Net entries | Dataset entries after preparation, potentially including repeated scans | `numTraining: 404` in the released combined T1 model |
| Distinct patients or MRI series | Individuals or acquisitions after resolving repetitions and cross-collection overlap | Requires case identifiers and provenance mapping |

The full MC-RC collection contains 124 ceT1 volumes, while the original SC-GK collection contains 242 T1 volumes. These are collection totals, not the training counts for every released model. [MC-RC collection](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/) · [SC-GK collection](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/)

### 7.2 Training and testing counts reported in the paper

Kujawa compared MC-RC, SC-GK, and combined training sources using T1, T2, and paired T1+T2 inputs. The study used an approximately 80:20 patient-separated development/test split, followed by five-fold cross-validation within development data. [Methods, §2.6](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

| Input | MC-RC training | SC-GK training | Combined training, as reported | MC-RC testing | SC-GK testing | Tilburg testing |
|---|---:|---:|---:|---:|---:|---:|
| ceT1 | 52 | 196 | 248 | 12 | 46 | 105 |
| T2 | 291 | 196 | 248* | 72 | 46 | 32 |
| ceT1 + T2 | 48 | 196 | 248* | 12 | 46 | Not available |

Source: [Kujawa et al., Table 2](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2).

Tilburg’s 105 ceT1 challenge-training scans and 32 private T2 validation scans served as this study’s external tests. No paired Tilburg evaluation was available. [Dataset description, §2.4](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

**Read the table as reported experimental counts.** Do not assume that every available T1 volume entered the T1-only experiment.

### 7.3 Published counts versus released model metadata

Table 2 reports **248** training cases for all three combined models. However, the component sums and released model metadata differ:

| Input | Component sum from Table 2 | Combined count printed in Table 2 | Released `numTraining` |
|---|---:|---:|---:|
| T1 | `52 + 196 = 248` | 248 | **404** |
| T2 | `291 + 196 = 487` | 248 | **487** |
| T1 + T2 | `48 + 196 = 244` | 248 | **388** |

The paper’s counts and the prepared model entries are different reporting levels. Preserve both rather than silently replacing the published values.

The T2 and T1+T2 combined counts printed in Table 2 remain discrepancies requiring clarification. The released metadata supplies the prepared-entry counts, but does not establish distinct patient or acquisition totals. [Kujawa et al., Table 2](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

Similarly, the reported MC-RC T1 split totals **64 cases** (`52 + 12`), rather than the collection’s 124 ceT1 volumes. Exact inclusion criteria and case identifiers should be checked before claiming all 124 volumes entered that experiment.

### 7.4 Released model metadata and inferred balancing

The following values were transcribed from project screenshots of the downloaded models’ `dataset.json` files:

| Model directory | Input channels | Observed `numTraining` |
|---|---|---:|
| `Dataset920_VSMCRCSCGKT1` | T1 | **404** |
| `Dataset921_VSMCRCSCGKT2` | T2 | **487** |
| `Dataset922_VSMCRCSCGKT1T2` | T1 and T2 | **388** |

The files were inspected under `nnUNetTrainer__nnUNetPlans__3d_fullres/`.

**Model download:** [Kujawa’s official Zenodo release](https://zenodo.org/records/10363647).

All three descriptions mention combining MC-RC and SC-GK cases, with cases repeated for balancing. The paper also describes balanced sampling between cohorts. [Methods, §2.6.1](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

#### Reconstruction matching all three totals

| Input | MC-RC component | SC-GK component | Inferred MC-RC representations per original case | Reconstructed total |
|---|---:|---:|---:|---:|
| T1 | 52 | 196 | **4** | `52 × 4 + 196 = 404` |
| T2 | 291 | 196 | **1** | `291 + 196 = 487` |
| T1 + T2 | 48 | 196 | **4** | `48 × 4 + 196 = 388` |

This supports the interpretation that:

- **T1:** the smaller MC-RC subset was represented four times, producing 208 MC-RC entries alongside 196 SC-GK entries.
- **T2:** the larger MC-RC subset was retained without expansion, producing 291 MC-RC entries alongside 196 SC-GK entries.
- **T1+T2:** the smaller paired MC-RC subset was represented four times, producing 192 MC-RC entries alongside 196 SC-GK entries.

Four representations means the original plus three additional representations—not four extra copies.

The T1 and paired T1+T2 reconstructed datasets are nearly balanced between cohorts. The T2 reconstruction is not an exactly equal-size balance.

#### Confirmed observations versus inferred implementation

**Confirmed from the supplied screenshots:**

- The prepared-entry totals are **404, 487, and 388**.
- The descriptions explicitly mention repeated cases for balancing.

**Inferred from the arithmetic:**

- MC-RC was represented four times for T1 and T1+T2.
- Neither cohort was expanded for T2.
- SC-GK retained 196 entries in each combination.

All three reconstructions match exactly, making this interpretation substantially stronger than an explanation based on the T1 total alone. Nevertheless, individual case identifiers have not been audited.

The T2 description contains the same generic repetition wording. Its total matches the unrepeated component sum, so that wording alone should not be treated as proof that T2 cases were duplicated.

A training manifest, `splits_final.json` if available, or author confirmation would establish exact membership, repetition multiplicity, and deduplication.

#### What `numTraining` counts

nnU-Net checks `numTraining` against the number of prepared dataset entries. It does not deduplicate them by patient or image content. [Dataset verification implementation](https://github.com/MIC-DKFZ/nnUNet/blob/master/nnunetv2/experiment_planning/verify_dataset_integrity.py)

For the two-channel model, **one case entry contains both T1 and T2**. Therefore, 388 means 388 prepared paired cases—not 388 individual MRI volumes or 388 verified unique patients.

The field also does not automatically give the number of entries used to fit each individual cross-validation fold.

### 7.5 How cross-collection overlap affects counting

The paper reports **58 shared patients but eight identical MRI series** between MC-RC and SC-GK. Patients with shared series were assigned to the respective training partitions. [Overlap and split handling, §§2.3.1 and 2.6.1](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

These statements do not establish complete deduplication of the combined training entries.

Therefore:

- Do not subtract shared patients from a count of MRI volumes.
- Do not assume all eight shared series are T1.
- Do not call summed training entries “unique patients.”
- Resolve patient overlap, identical acquisitions, and balancing repetitions separately.

### 7.6 Do these counts imply inclusion of the private London extension?

**The metadata does not establish inclusion of the additional 137 private London patients.**

The reported component counts reproduce all three released totals using the inferred balancing pattern:

```text
T1:    52 × 4 + 196 = 404
T2:   291     + 196 = 487
T1+T2: 48 × 4 + 196 = 388
```

Additional private cases are not needed to explain these totals. However, numerical consistency is not a case-level provenance audit and cannot establish the inclusion or exclusion of particular patients.

For reporting these models:

> The released combined models declare 404 T1, 487 T2, and 388 paired T1+T2 training entries. These totals are consistent with fourfold representation of the MC-RC T1 and T1+T2 subsets and an unrepeated T2 combination. Exact case membership, multiplicity, and deduplication remain unverified. The counts do not establish inclusion of the additional private London challenge cohort.

### 7.7 Implications for evaluation in this repository

Before evaluating a pretrained model:

1. Identify the source patients used to develop that model.
2. Resolve overlap with the intended evaluation cohort.
3. Distinguish held-out study tests from cross-validation validation cases.
4. Keep repeated entries associated with their original acquisition.
5. Describe an evaluation on training-source patients as such.

A pretrained model’s `dataset.json` provides useful context, but a single aggregate count cannot establish whether a proposed test subject was unseen.
## 8. Overlap and dataset splitting

Kujawa reports **58 overlapping patients and eight shared MRI series** between MC-RC and the original SC-GK dataset. TCIA provides a mapping file. [Kujawa et al., §2.3.1](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full#s2)

For this repository:

1. Assign all examinations from a patient to the same partition.
2. Keep a patient’s T1 and T2 together.
3. Keep longitudinal visits together.
4. Resolve cross-collection patient mappings before splitting.
5. Treat different challenge editions as overlapping releases.
6. Preserve original identifiers and document any renumbering.
7. Record whether labels came from TCIA contours or a challenge release.

A renamed NIfTI file is not evidence of a new patient. A changed mask is not evidence of an independent image.

Recommended provenance fields:

```text
dataset_release
release_version
original_subject_id
original_series_uid
modality
examination_id
challenge_edition
challenge_split
annotation_release
structure_name
target_space
conversion_method
```

## 9. This repository’s conversion policy

### Target outputs

Each patient should have the following outputs when annotations are available:

| Space | Image | VS mask | Cochlea mask |
|---|---|---|---|
| T1 | Native T1 | VS on T1 grid | Cochlea on T1 grid |
| T2 | Native T2 | VS on T2 grid | Cochlea on T2 grid |

### Prefer contours already in the target space

Apply this rule separately to each structure:

1. Use the target space’s JSON contour when present.
2. If absent there but present in the other space, transform the other contour’s points into the target space before discretization.
3. If absent in both, record it as unavailable.
4. Treat malformed contour data as an error.

Keep both image volumes on their native grids.

Record the source coordinate frame, target grid, method, transform file, and foreground count in `export_manifest.json`. Record original drawing modality as unknown unless independently established.

### Output layout

```text
vs_242_nifti/
└── vs_gk_<subject_number>/
    ├── vs_gk_t1_refT1.nii.gz
    ├── vs_gk_tv_refT1.nii.gz       # or vs_gk_an_refT1.nii.gz
    ├── vs_gk_cochlea_refT1.nii.gz  # when available
    ├── vs_gk_t2_refT2.nii.gz
    ├── vs_gk_tv_refT2.nii.gz       # or vs_gk_an_refT2.nii.gz
    ├── vs_gk_cochlea_refT2.nii.gz  # when available
    ├── additional_structure_masks...
    └── export_manifest.json
```

The filenames describe this repository’s exports; they are not official crossMoDA naming conventions.

### Structure handling

| Exported name | Repository interpretation |
|---|---|
| `TV` | Final VS annotation |
| `AN` | Alternative VS label, based on project annotation review |
| `Vol2016` | Preliminary semiautomated VS segmentation before refinement to TV, based on project clarification |
| `Cochlea` | Cochlea annotation |
| Other names | Preserve and review before assigning a training class |

Do not automatically treat every `Vol...` structure as equivalent to `Vol2016`. Do not combine preliminary and refined VS masks.

### Verification

For each exported mask, check:

- shape and spatial mapping against its target image;
- binary values;
- foreground voxel count;
- axial, coronal, and sagittal alignment;
- provenance and any fallback operation.

Compare physical volumes, not raw T1/T2 voxel counts:

```text
Volume in mm³ = foreground voxel count × voxel volume in mm³
```

## 10. Findings from the converted inventory

**These are project-specific observations from `vs_242_segmentation_inventory.csv`, not official cohort statistics.**

| Inventory finding | Count |
|---|---:|
| Subjects with readable manifests | 242 |
| Exported files reported missing | 0 |
| Subjects with `TV` | 155 |
| Subjects with `AN` | 82 |
| Subjects with either `TV` or `AN` | 237 |
| Subjects with exactly `Cochlea`, ignoring capitalization | 145 |
| Subjects without that exact cochlea name | 97 |

All subjects had matching T1/T2 structure-name lists in this inventory.

Five subjects require additional tumor-label review:

| Subject | Relevant names |
|---|---|
| 8 | `tumour` |
| 20 | `Rt AN` |
| 63 | `Men`, `vol 2y` |
| 73 | `Men` |
| 159 | `TvT1` |

Cochlea exceptions:

- **236:** `Cochlea_c` and `Cochlea_d`.
- **177 and 181:** `Modiolus`, retained separately.

After accounting for subject 236’s alternate cochlea names, **96 subjects lack all three names `Cochlea`, `Cochlea_c`, and `Cochlea_d`**.

Use these as candidates for image review. Missing cochlea annotations alone do not establish postoperative status or fat packing.

### Literature exclusions requiring reconciliation

The supplied supplement to [Mehta et al.](https://doi.org/10.3174/ajnr.A9112) reports:

- exclusion of `vs_gk_131` from their T1 evaluation;
- 241 evaluated cases;
- 239 contrast-enhanced and two non-contrast scans;
- 193 preoperative and 48 postoperative scans;
- exclusion of `vs_gk_108_t1` only from composition subgrouping.

Our inventory contains nonempty TV masks for subject 131 and an `AN` annotation for subject 108. Reconcile images, identifiers, and study-specific exclusions before applying those exclusions here.

Keep image filenames as `t1`; do not assume contrast administration from the folder name alone.

## 11. Frequently confused points

### Is Tilburg’s 105-case set the crossMoDA 2021 training set?

**No.** The 2021 ceT1 set is London. Tilburg’s separate 105-case ceT1 contribution entered in 2022.

### Does “SC-GK” always mean 242 patients?

**No.** Specify whether it means the original public London release or the expanded challenge collection.

### Do I need 379 patients to have downloaded the original TCIA dataset completely?

**No.** Its published cohort is 242 patients.

### Are the additional 137 patients T2-only examinations?

The challenge tested on their T2 scans. Both T1 and T2 were acquired for the underlying patients.

### Does “unannotated” mean nobody made a manual segmentation?

Not necessarily. It can mean ground truth was withheld from challenge participants.

### Does the end of a competition make its private labels public?

No automatic release should be assumed. Check the current repository and organizer announcements.

### Can crossMoDA 2021 be independent external validation after training on all 242 TCIA patients?

Its public training/validation subsets overlap those patients. Establish overlap before calling any evaluation independent.

### Are challenge annotations identical to original TCIA annotations?

Not necessarily. Bilateral cochlea annotation and tumor subsegmentation introduce release-specific differences.

### Is MC-RC still only partially downloadable?

TCIA reports that previously embargoed images were released in June 2026. This update concerns the parent MC-RC collection; exact challenge labels and splits remain separate release questions.

## 12. Sources

Use dataset citations for downloaded data and paper citations for methods or scientific comparisons.

1. **Shapey et al. — original London dataset.**  
   [TCIA collection](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-seg/) · [Dataset DOI](https://doi.org/10.7937/TCIA.9YTJ-5Q73)

2. **Shapey et al., 2021 — dataset paper.**  
   *Segmentation of vestibular schwannoma from MRI, an open annotated dataset and baseline algorithm.*  
   [DOI](https://doi.org/10.1038/s41597-021-01064-w) · [Open PDF](https://discovery.ucl.ac.uk/id/eprint/10137674/1/s41597-021-01064-w.pdf)

3. **Kujawa et al. — MC-RC dataset and current release notes.**  
   [TCIA collection](https://www.cancerimagingarchive.net/collection/vestibular-schwannoma-mc-rc/) · [Dataset DOI](https://doi.org/10.7937/hrzh-2n82)

4. **Kujawa et al., 2024 — comparative dataset study.**  
   *Deep learning for automatic segmentation of vestibular schwannoma: a retrospective study from multi-center routine MRI.*  
   [Full paper](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2024.1365727/full)

5. **Dorent et al., 2023 — crossMoDA 2021 paper.**  
   *CrossMoDA 2021 challenge: Benchmark of cross-modality domain adaptation techniques for vestibular schwannoma and cochlea segmentation.*  
   [DOI](https://doi.org/10.1016/j.media.2022.102628) · [Open manuscript](https://arxiv.org/html/2201.02831)

6. **Wijethilake et al., 2025 manuscript — challenge retrospective.**  
   *crossMoDA Challenge: Evolution of Cross-Modality Domain Adaptation Techniques for Vestibular Schwannoma and Cochlea Segmentation from 2021 to 2023.*  
   [Manuscript and split table](https://arxiv.org/html/2506.12006v1)

7. **Official challenge releases.**  
   [2021 Zenodo](https://zenodo.org/records/4662239) · [2022 Zenodo](https://zenodo.org/records/6504722) · [2023 Synapse](https://www.synapse.org/Synapse:syn51236108)

8. **Official challenge website.**  
   [Tasks, acquisition descriptions, and organizer contact](https://crossmoda-challenge.ml/)

9. **Original preprocessing repository.**  
   [KCL-BMEIS/VS_Seg preprocessing](https://github.com/KCL-BMEIS/VS_Seg/tree/master/preprocessing)

10. **Mehta et al., 2025 — external T1 evaluation.**  
    *Comparative Evaluation of Deep Learning Models for 3D Segmentation and Volumetry of Vestibular Schwannomas Using Large Heterogeneous Datasets with External Validation.*  
    [DOI](https://doi.org/10.3174/ajnr.A9112)  
    Project notes above use the supplied supplemental excerpt.

11. **Local provenance.**  
    `export_manifest.json` files and `vs_242_segmentation_inventory.csv` document the actual conversion and structure inventory used in this repository.
