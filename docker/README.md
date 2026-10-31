# Run the complete pipeline locally with Docker

[Main README](../README.md)

The image processes contrast-enhanced T1-weighted DICOM images through VS segmentation, brainstem segmentation, false-positive correction, measurements, and review DICOM generation. Both trained models and their dependencies are included.

## 1. Pull the image

Use Docker with Linux containers on an x86-64 machine. On Windows, run these commands in WSL Bash with Docker Desktop integration enabled.

```bash
IMAGE="ghcr.io/bao-bui/vs-pipeline:0.2.2"
docker pull "$IMAGE"
```

CPU and GPU execution use the same image. GPU execution requires a compatible NVIDIA GPU and driver, with Docker GPU access configured for the image's CUDA 13.0 runtime.

## 2. Check the installation

CPU:

```bash
docker run --rm "$IMAGE" --check --device cpu --threads 8
```

GPU:

```bash
docker run --rm --gpus all \
  "$IMAGE" --check --device cuda --threads 2
```

These checks verify model-file availability, predictor imports, and a small device calculation. They do not load model checkpoints or run segmentation.

## 3. Set input and output paths

Use absolute paths. Process one patient's DICOM images at a time, and keep the results outside the input directory.

```bash
INPUT="/absolute/path/to/patient-dicoms"
RESULTS="/absolute/path/to/vs-pipeline-results"
CASE="VS_CASE_001"

mkdir -p "$RESULTS"
OUTPUT="$(mktemp -d "$RESULTS/${CASE}_XXXXXX")"
```

The output directory must be empty when the pipeline starts. Create a new output directory for each run.

On Windows through WSL, for example:

```bash
INPUT="/mnt/c/Users/YOUR_USERNAME/Downloads/patient-dicoms"
RESULTS="/mnt/c/Users/YOUR_USERNAME/Downloads/vs-pipeline-results"
CASE="VS_CASE_001"

mkdir -p "$RESULTS"
OUTPUT="$(mktemp -d "$RESULTS/${CASE}_XXXXXX")"
```

## 4. Select the contrast-enhanced T1 series

List the available DICOM series:

```bash
docker run --rm \
  --mount "type=bind,source=$INPUT,target=/input,readonly" \
  "$IMAGE" --list-series
```

Copy the desired Series Instance UID:

```bash
SERIES_UID="REPLACE_WITH_SELECTED_SERIES_INSTANCE_UID"
```

If the input contains only the intended T1ce series, you can omit `--series-uid` from the execution command.

The case identifier labels the processing run; it does not anonymize DICOM metadata.

## 5. Run the pipeline

Choose either GPU or CPU execution.

GPU:

```bash
set -o pipefail

docker run --rm --gpus all --shm-size=2g \
  --mount "type=bind,source=$INPUT,target=/input,readonly" \
  --mount "type=bind,source=$OUTPUT,target=/output" \
  "$IMAGE" \
  --input /input --output /output \
  --device cuda --threads 2 \
  --case "$CASE" --series-uid "$SERIES_UID" \
  2>&1 | tee "${OUTPUT}.log"
```

CPU:

```bash
set -o pipefail

docker run --rm --cpus=8 --shm-size=2g \
  --mount "type=bind,source=$INPUT,target=/input,readonly" \
  --mount "type=bind,source=$OUTPUT,target=/output" \
  "$IMAGE" \
  --input /input --output /output \
  --device cpu --threads 8 \
  --case "$CASE" --series-uid "$SERIES_UID" \
  2>&1 | tee "${OUTPUT}.log"
```

Adjust CPU allocation and thread count to match your machine. Both modes use all five folds of each model. No separate model download or mount is required.

The image handles legacy brainstem checkpoint loading internally.

Temporary processing files use the container's filesystem by default, which needs sufficient free disk space. They are removed after a successful run. With `--rm`, any remaining container-local files are also removed when the container exits; the host log is retained.

## 6. Review the outputs

Results are written directly into four folders:

```text
output/
├── axial/
│   └── IM_*.dcm
├── montage/
│   └── IM_*.dcm
├── nifti/
│   ├── input_mri.nii
│   ├── vs_raw.nii
│   ├── brainstem.nii
│   └── vs_corrected.nii
└── json/
    ├── report.json
    ├── timings.json
    ├── export_metadata.json
    └── ...
```

| Folder | Contents |
| --- | --- |
| `axial/` | Individual axial overlay DICOMs |
| `montage/` | Multiplanar review montage DICOMs |
| `nifti/` | Canonical input MRI and available segmentation masks, exported as uncompressed `.nii` files |
| `json/` | Status, measurements, timings, source metadata, and other generated JSON files |

No ZIP archives are produced. JSON filenames from intermediate stages include their source-directory names to avoid collisions.

Measurements include volume in cm³ and maximum diameters in the axial, sagittal, and coronal planes.

Review `json/report.json`, the execution log, and the overlays in a DICOM viewer. If automatic component selection is unresolved, the pipeline can still provide raw component volumes, but calipers are unavailable. The `vs_corrected.nii` filename alone does not establish that correction succeeded; check the reported status. The brainstem mask may be absent if brainstem prediction failed.

## 7. Export a previously saved run without repeating inference

For an older run containing `dicom_results/`, `nifti/`, and `report.json`:

```bash
PREVIOUS="/absolute/path/to/saved-run"
OUTPUT="$(mktemp -d "$RESULTS/reexport_XXXXXX")"

docker run --rm \
  --mount "type=bind,source=$PREVIOUS,target=/previous,readonly" \
  --mount "type=bind,source=$OUTPUT,target=/output" \
  "$IMAGE" --export-only /previous --output /output
```

This copies the existing DICOMs and JSONs and decompresses available NIfTIs into the four-folder layout. It does not repeat inference or modify the saved run.
