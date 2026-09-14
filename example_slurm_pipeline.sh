#!/usr/bin/env bash
# Example SLURM pipeline for:
# https://github.com/Bao-Bui/VS_segmentation_correction
#
# Workflow:
#   1. Vestibular schwannoma segmentation with nnU-Net v2
#   2. Brainstem segmentation with nnU-Net v1
#   3. False-positive correction using the predicted brainstem mask
#   4. Tumor size/diameter metric calculation
#
# IMPORTANT:
#   - The SLURM resource requests below are examples. Edit them for your HPC.
#   - This example assumes nnU-Net v1 and v2 are available in one Conda
#     environment.

#SBATCH --job-name=vs_segmentation_pipeline
#SBATCH --partition=gpu                 # EDIT: your GPU partition name
#SBATCH --gres=gpu:1                    # EDIT: your site's GPU resource syntax
#SBATCH --cpus-per-task=32              # EDIT for your cluster
#SBATCH --mem=256G                      # EDIT for your cluster
#SBATCH --time=12:00:00                 # EDIT for your cluster
#SBATCH --output=vs_pipeline_%j.out
#SBATCH --error=vs_pipeline_%j.err

set -euo pipefail

# =============================================================================
# USER CONFIGURATION
# =============================================================================
# Edit these paths for your system before submitting the job.

# WORK_DIR hierarchy
#
# /path/to/workdir/
# ├── nnUNet_raw_data_base/
# │   └── nnUNet_raw_data/
# │       └── Task600_Brainstem/
# │           └── imagesTs/
# │               ├── VS_001_0000.nii.gz
# │               ├── VS_002_0000.nii.gz
# │               └── ...
# └── vs_pipeline_outputs/              # created automatically
#     ├── raw_tumor/
#     ├── brainstem/
#     └── post_processed/
#
# Additional nnU-Net cache/preprocessed/temp directories are created
# automatically under WORK_DIR as needed.

WORK_DIR="/path/to/workdir"
VS_MODEL="/path/to/MC-RC+SC-GK-models"
BS_MODEL="/path/to/nnUNet1_brainstem_model"
CONDA_ENV="/path/to/nnunet_conda_env"

# Expected input location for T1 post-contrast scans.
# Input files should follow nnU-Net single-channel naming, for example:
#   VS_001_0000.nii.gz
#   VS_002_0000.nii.gz
NNUNET_RAW_BASE="${WORK_DIR}/nnUNet_raw_data_base"
INPUT_DIR="${NNUNET_RAW_BASE}/nnUNet_raw_data/Task600_Brainstem/imagesTs"

# Pipeline outputs.
OUTPUT_ROOT="${WORK_DIR}/vs_pipeline_outputs"
RAW_TUMOR_OUTPUT="${OUTPUT_ROOT}/raw_tumor"
BRAINSTEM_OUTPUT="${OUTPUT_ROOT}/brainstem"
POSTPROCESSED_OUTPUT="${OUTPUT_ROOT}/post_processed"

mkdir -p \
    "$RAW_TUMOR_OUTPUT" \
    "$BRAINSTEM_OUTPUT" \
    "$POSTPROCESSED_OUTPUT"

# =============================================================================
# BASIC VALIDATION
# =============================================================================

for dir in "$WORK_DIR" "$VS_MODEL" "$BS_MODEL" "$INPUT_DIR"; do
    if [[ ! -d "$dir" ]]; then
        echo "ERROR: Required directory not found: $dir" >&2
        exit 1
    fi
done

if ! find "$INPUT_DIR" -maxdepth 1 -type f -name '*_0000.nii.gz' -print -quit | grep -q .; then
    echo "ERROR: No *_0000.nii.gz scans found in: $INPUT_DIR" >&2
    exit 1
fi

# =============================================================================
# CONDA INITIALIZATION
# =============================================================================
# Module names are site-specific. If your HPC requires a Conda/Anaconda module,
# load it here, for example:
#
#   module load anaconda3

if ! command -v conda >/dev/null 2>&1; then
    echo "ERROR: 'conda' is not available in PATH." >&2
    echo "Load your site's Conda/Anaconda module before running this script." >&2
    exit 1
fi

# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"

if ! command -v nnUNetv2_predict >/dev/null 2>&1; then
    echo "ERROR: nnUNetv2_predict was not found in: $CONDA_ENV" >&2
    exit 1
fi

if ! command -v nnUNet_predict >/dev/null 2>&1; then
    echo "ERROR: nnUNet_predict was not found in: $CONDA_ENV" >&2
    exit 1
fi

# =============================================================================
# JOB-SPECIFIC CACHE / TEMP DIRECTORIES
# =============================================================================
# Keeping temporary/cache files inside WORK_DIR can be useful on HPC systems
# where compute nodes have limited or no access to the user's home directory.

JOB_TAG="${SLURM_JOB_ID:-manual_$$}"
CACHE_ROOT="${WORK_DIR}/.cache/vs_pipeline/${JOB_TAG}"
TMPDIR="${WORK_DIR}/tmp/vs_pipeline/${JOB_TAG}"

export TMPDIR
export XDG_CACHE_HOME="${CACHE_ROOT}/xdg"
export MPLCONFIGDIR="${CACHE_ROOT}/matplotlib"
export TORCHINDUCTOR_CACHE_DIR="${CACHE_ROOT}/torchinductor"
export HF_HOME="${CACHE_ROOT}/huggingface"
export nnUNet_compile=True

mkdir -p \
    "$TMPDIR" \
    "$XDG_CACHE_HOME" \
    "$MPLCONFIGDIR" \
    "$TORCHINDUCTOR_CACHE_DIR" \
    "$HF_HOME"

# If compute nodes on your HPC cannot access the normal home directory,
# uncomment the following two lines:
# export HOME="${WORK_DIR}/home"
# mkdir -p "$HOME"

cleanup() {
    rm -rf "$CACHE_ROOT" "$TMPDIR"
}
trap cleanup EXIT

# =============================================================================
# STEP 1: VESTIBULAR SCHWANNOMA SEGMENTATION (nnU-Net v2)
# =============================================================================

echo "=== Step 1/4: VS segmentation with nnU-Net v2 ==="

export nnUNet_raw="${WORK_DIR}/nnUNet_v2_raw"
export nnUNet_preprocessed="${WORK_DIR}/nnUNet_v2_preprocessed"
export nnUNet_results="$VS_MODEL"

mkdir -p "$nnUNet_raw" "$nnUNet_preprocessed"

nnUNetv2_predict \
    -d 920 \
    -f 0 1 2 3 4 \
    -tr nnUNetTrainer \
    -c 3d_fullres \
    -p nnUNetPlans \
    -i "$INPUT_DIR" \
    -o "$RAW_TUMOR_OUTPUT"

# =============================================================================
# STEP 2: BRAINSTEM SEGMENTATION (nnU-Net v1)
# =============================================================================

echo "=== Step 2/4: Brainstem segmentation with nnU-Net v1 ==="

export nnUNet_raw_data_base="$NNUNET_RAW_BASE"
export nnUNet_preprocessed="${WORK_DIR}/nnUNet_v1_preprocessed"
export RESULTS_FOLDER="$BS_MODEL"

mkdir -p "$nnUNet_preprocessed"

nnUNet_predict \
    -i "$INPUT_DIR" \
    -o "$BRAINSTEM_OUTPUT" \
    -tr nnUNetTrainerV2 \
    -m 3d_fullres \
    -p nnUNetPlansv2.1_24GB \
    -t Task600_Brainstem \
    -f 0 1 2 3 4

# =============================================================================
# STEP 3: FALSE-POSITIVE CORRECTION
# =============================================================================

echo "=== Step 3/4: False-positive correction ==="

python /path/to/vs_false_positive_correction.py \
    --tumor "$RAW_TUMOR_OUTPUT" \
    --brainstem "$BRAINSTEM_OUTPUT" \
    --out "$POSTPROCESSED_OUTPUT"

# =============================================================================
# STEP 4: SIZE / DIAMETER METRICS
# =============================================================================

echo "=== Step 4/4: Calculating tumor metrics ==="

python /path/to/calculate_mask_metrics_internal_chord_contour.py "$POSTPROCESSED_OUTPUT"

echo "=== Pipeline complete ==="
echo "Raw VS masks:          $RAW_TUMOR_OUTPUT"
echo "Brainstem masks:       $BRAINSTEM_OUTPUT"
echo "Post-processed masks:  $POSTPROCESSED_OUTPUT"
