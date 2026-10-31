# Example SLURM Pipeline

[Main README](../README.md)

For users running this workflow on a high-performance computing (HPC) cluster managed by [SLURM](https://slurm.schedmd.com/), an example batch script is provided in [`example_slurm_pipeline.sh`](example_slurm_pipeline.sh). This script combines the major steps described in the [main README](../README.md) into a single GPU job:

1. **Vestibular schwannoma segmentation** using the Kujawa et al. nnU-Net v2 model.
2. **Brainstem segmentation** using the Gesierich et al. nnU-Net v1 model.
3. **False-positive correction** using `vs_false_positive_correction.py`.
4. **Tumor size and diameter calculation** using `calculate_mask_metrics_maximum_diameter.py`.

The script is intended as a **template rather than a cluster-independent executable**. SLURM configurations, software modules, storage locations, and GPU resource syntax vary between HPC systems. Users should therefore modify the paths and SLURM resource requests before submitting the job.

## 1. Configure the SLURM resources

At the beginning of `example_slurm_pipeline.sh`, modify the `#SBATCH` directives according to the resources available on your cluster. For example:

```bash
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=32
#SBATCH --mem=256G
#SBATCH --time=12:00:00
```

In particular, the GPU partition name and GPU allocation syntax may differ between institutions. Consult your HPC documentation or system administrator if necessary.

The output and error logs are written to the directory from which the job is submitted:

```bash
#SBATCH --output=vs_pipeline_%j.out
#SBATCH --error=vs_pipeline_%j.err
```

where `%j` is replaced by the SLURM job ID.

## 2. Configure the working directory, models, and Conda environment

Edit the following paths in the `USER CONFIGURATION` section:

```bash
WORK_DIR="/path/to/workdir"
VS_MODEL="/path/to/MC-RC+SC-GK-models"
BS_MODEL="/path/to/nnUNet1_brainstem_model"
CONDA_ENV="/path/to/nnunet_conda_env"
```

- `WORK_DIR` is the main directory containing the input scans and pipeline outputs.
- `VS_MODEL` should point to the extracted Kujawa et al. nnU-Net v2 model described in **Step 1**.
- `BS_MODEL` should point to the extracted Gesierich et al. nnU-Net v1 brainstem model described in **Step 2**.
- `CONDA_ENV` should point to the Conda environment containing the required Python packages, nnU-Net v1, and nnU-Net v2.

The example script assumes that both nnU-Net versions can be called from the same Conda environment. If your installation uses separate environments, the activation commands can be modified accordingly.

## 3. Set up the input directory

The expected `WORK_DIR` hierarchy is:

```text
/path/to/workdir/
├── nnUNet_raw_data_base/
│   └── nnUNet_raw_data/
│       └── Task600_Brainstem/
│           └── imagesTs/
│               ├── VS_001_0000.nii.gz
│               ├── VS_002_0000.nii.gz
│               └── ...
└── vs_pipeline_outputs/              # created automatically
    ├── raw_tumor/
    ├── brainstem/
    └── post_processed/
```

Place the contrast-enhanced T1-weighted NIfTI scans to be processed in:

```text
WORK_DIR/nnUNet_raw_data_base/nnUNet_raw_data/Task600_Brainstem/imagesTs/
```

As described in the [main README](../README.md), each single-channel input image must follow nnU-Net naming conventions:

```text
{case_identifier}_0000.nii.gz
```

For example:

```text
VS_001_0000.nii.gz
VS_002_0000.nii.gz
VS_003_0000.nii.gz
```

The `vs_pipeline_outputs` directory and its subdirectories are created automatically when the job begins.

## 4. Specify the locations of the post-processing scripts

The following two lines in `example_slurm_pipeline.sh` must also be changed to the locations of the corresponding scripts on your system:

```bash
python /path/to/vs_false_positive_correction.py \
```

and

```bash
python /path/to/calculate_mask_metrics_maximum_diameter.py "$POSTPROCESSED_OUTPUT"
```

For example, if this repository has been cloned to `/path/to/VS_segmentation_correction`, these may be changed to:

```bash
python /path/to/VS_segmentation_correction/vs_false_positive_correction.py
```

and

```bash
python /path/to/VS_segmentation_correction/calculate_mask_metrics_maximum_diameter.py
```

## 5. Configure Conda on your HPC

The script initializes Conda using:

```bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"
```

Some HPC systems require a software module to be loaded before the `conda` command becomes available. If so, add the appropriate module command before Conda initialization. For example:

```bash
module load anaconda3
```

The correct module name is institution-specific.

The script checks that both:

```bash
nnUNetv2_predict
```

and

```bash
nnUNet_predict
```

are available after the Conda environment is activated. If either executable cannot be found, the job will terminate before inference begins.

## 6. Cache and temporary files

The example script stores temporary and cache files inside `WORK_DIR` rather than assuming that compute nodes have unrestricted access to the user's home directory. Job-specific cache and temporary directories are created using the SLURM job ID and automatically removed when the job exits.

For HPC systems where compute nodes cannot access the normal home directory, the following lines in the script can also be uncommented:

```bash
export HOME="${WORK_DIR}/home"
mkdir -p "$HOME"
```

This behavior may not be necessary on all systems.

## 7. Submit the pipeline

Once the paths and SLURM settings have been configured, submit the job from this folder:

```bash
sbatch example_slurm_pipeline.sh
```

The complete workflow will then run sequentially within the same SLURM job.

After successful completion, the main outputs will be stored under:

```text
WORK_DIR/vs_pipeline_outputs/
├── raw_tumor/          # Original nnU-Net v2 VS predictions
├── brainstem/          # nnU-Net v1 brainstem predictions
└── post_processed/     # VS masks after false-positive correction
```

The size and diameter metrics are subsequently calculated from the corrected masks in `post_processed`.

Users should inspect the SLURM `.out` and `.err` files after execution to confirm that each stage completed successfully. Because HPC environments differ substantially in module systems, filesystem organization, CUDA configuration, and SLURM resource definitions, `example_slurm_pipeline.sh` should be treated as a working example that can be adapted to the local computing environment rather than as a universal SLURM configuration.
