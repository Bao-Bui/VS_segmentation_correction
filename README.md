# Correction of False Positives in Automated Vestibular Schwannoma (VS) Segmentation
Notes: The following procedure only works for contrast-enhanced-T1-weghted scans. The brainstem segmentation model used in `Step 2` was trained on only T1 images.

## Step 1: VS Segmentation
The model used was that of Kujawa et al., 2024.
```
Kujawa, A., Dorent, R., Connor, S., Thomson, S., Ivory, M., Vahedi, A., Guilhem, E., Wijethilake, N., Bradford, R., Kitchen, N., Bisdas, S., Ourselin, S., Vercauteren, T., & Shapey, J. (2024).
Deep learning for automatic segmentation of vestibular schwannoma: A retrospective study from multi-center routine MRI. Frontiers in Computational Neuroscience, 18, 1365727.
https://doi.org/10.3389/fncom.2024.1365727

```
Below is a step-by-step instruction on how to implement this model:
### 1. Download and unzip `MC-RC+SC-GK-models.zip` from the following repository
```
Aaron Kujawa, Dorent, R., Wijethilake, N., Connor, S., Thomson, S., Ivory, M., Bradford, R., Kitchen, N., Bisdas, S., Ourselin, S., Vercauteren, T., & Shapey, J. (2023).
Deep Learning for Automatic Segmentation of Vestibular Schwannoma: A Retrospective Study from Multi-Centre Routine MRI -- Deep learning models. Zenodo.
https://doi.org/10.5281/ZENODO.10363647
```
This model runs on the framework of nnU-net V2, whose Github repository and original paper are as follows
```
Original Paper: Isensee, F., Jaeger, P. F., Kohl, S. A. A., Petersen, J., & Maier-Hein, K. H. (2021).
nnU-Net: A self-configuring method for deep learning-based biomedical image segmentation. Nature Methods, 18(2), 203–211.
https://doi.org/10.1038/s41592-020-01008-z

Github: https://github.com/MIC-DKFZ/nnUNet
```
### 2. Install nnU-net V2
  * Follow the instructions here: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/installation_instructions.md
  * Make sure you download Pytorch first, choosing a Torch version that is compatible with your CUDA version (https://pytorch.org/get-started/previous-versions/). I used torch2.7.1 on CUDA 12.6, which requires python>=3.9.
  * As the developers note, it is strongly recommended that you install nnU-Net V2 in a virtual environment (pip or conda) due to possible interferences with nnU-net V1 used in `Step 2`
### 3. Set up the nnunet environments in the terminal
  * `nnUNet_raw` can be set to a random path and does not mater unless you're training a new model.
  * `nnUNet_preprocessed` can be set to a random path and does not mater unless you're training a new model.
  * `nnUNet_results` must be set to the location where the trained models are stored. This should be the unzipped folder that contains three trained models (T1, T2, and mixed).
  * For more information, check out: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/setting_up_paths.md
### 4. Set up the folder containing the T1 scans to be run inference on
  * Although nnU-net V2 supports many file formats, it is conventional to run inferences on NIfTI files. NIfTI conversion from DICOM files can be done using `3DSlicer` or `dcm2nii`.
  * For your convenience, the `input_folder` for nnU-net V2 is the same as `nnUNet_raw_data_base/nnUNet_raw_data/Task600_Brainstem/imagesTs` in nnU-net V1 
  * For models that were trained on only one imaging modality (e.g., the one used below), imaging files in the `input_folder` must have the naming format of `{case_identifier}_0000.nii.gz`. For example:
```
 input_folder
 ├── VS_001_0000.nii.gz
 ├── VS_002_0000.nii.gz
 ├── VS_003_0000.nii.gz
 ├── ...
```
  * For the MCRC-SCGK T1 3d_fullres model that will be used below, _0000 indicates to the model that the images in the `input_folder` are T1 images, as specified by the `dataset.json` file in the trained model.
  * For more information on the formatting of `input_folder`, check out: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format_inference.md
  * For more information on modality indicators (or channel names as nnU-net V2 calls it), check out: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format.md
### 5. Run the following inference prompt in the terminal
```
nnUNetv2_predict -d Dataset920_VSMCRCSCGKT1 -i path_to_input_folder -o path_to_tumor_output_folder -f  0 1 2 3 4 -tr nnUNetTrainer -c 3d_fullres -p nnUNetPlan
```
Assuming the input folder looks like the example above, you'll find the automated segmentation tumor masks in the tumor_output_folder in the following format if inference was run successfully:
```
 tumor_output_folder
 ├── VS_001.nii.gz
 ├── VS_002.nii.gz
 ├── VS_003.nii.gz
 ├── ...
```
This specific T1 model from Kujawa et al. gives the best results according to the performance metrics reported in their paper.

## Step 2: Brainstem Segmentation
The model used was that of Gesierich et al., 2025.
```
Gesierich, B., Sander, L., Pirpamer, L., Meier, D. S., Ruberte, E., Amann, M., Sinnecker, T., Huck, A., De Leeuw, F., Maillard, P., Moy, S., Helmer, K. G., MarkVCID Consortium, Levin, J., Höglinger, G. U., PROMESA Study Group, Kühne, M., Bonati, L. H., Kuhle, J., … Duering, M. (2025).
Extended Technical and Clinical Validation of Deep Learning‐Based Brainstem Segmentation for Application in Neurodegenerative Diseases. Human Brain Mapping, 46(3), e70141.
https://doi.org/10.1002/hbm.70141
```
Below is a step-by-step instruction on how to implement this model:
### 1. Download and extract `nnUNet_brainstem.tar.gz` from the following repository
```
Gesierich, B., & Duering, M. (2024). Deep learning-based brainstem segmentation: nnU-Net model (Version 1.0.2). Zenodo.
https://doi.org/10.5281/ZENODO.13323293
```
This model runs on the framework of nnU-net V1. See Github repository: https://github.com/Gitsamshi/nnUNet-1

### 2. Install nnU-net V1.7.1
  * nnU-net V1 and nnU-net2 can be installed concurrently on a local machine (https://github.com/MIC-DKFZ/nnUNet/releases). To avoid dependecy issues, they may be built in different virtual environments. Nevertheless, I managed to run both in the same virtual environment.
  * Again, make sure you download Pytorch first (see above) in the new virtual environment.
  * Because nnU-net V1.7.1 is deprecated, your python wheel may have trouble resolving dependencies. Furthermore, you will have to make some minor modifications to the source code later (see below). Thus, it is recommended that you clone the Github repository onto your local machine and install it from there. This requires that you have Git installed on your local machine (https://git-scm.com/downloads). Below is an example on how to do this using pip, although conda works as well:
```
pip3 -m venv nnunet1_env
cd nnunet1_env
git clone https://github.com/MIC-DKFZ/nnUNet.git
cd nnUNet
pip install -e .
```
### 3. Code modifications (Windows only)
  * Depending on your nnU-Net version, you may have the following issue. For torch>=2.6, the default for `torch.load()` is `weights_only = True`. If that is the case, make sure to add `weights_only = False` to the `torch.load()` function in `nnUnet/nnunet/training/model_restore.py`. For more information, see https://docs.pytorch.org/docs/stable/notes/serialization.html#weights-only.
  * For Windows machines that use the `spawn` start method, lambda functions is not pickle-able. This is not an issue for Linux/macOS because these OS's use `fork` (which just copies the entire memory without pickling). One way to fix this is to replace the `lambda x: x` function in `nnUNet/nnunet/training/network_training/nnUNetTrainerV2.py` and `nnUNet/nnunet/network_architecture/generic_UNet.py` with `torch.nn.Identity()` which basically does the same thing.
  * Similarly in `nnUNet/nnunet/utilities/nd_softmax.py`, `softmax_helper = lambda x: F.softmax(x, 1)` should be replaced with the function below. 
```
def softmax_helper(x):
    import torch
    return torch.nn.functional.softmax(x, 1)
```
  * There are more lambda functions throughout the package. Feel free to make changes if needed, but the aforementioned modifications should resolve the issues for Windows users.
### 4. Set up the nnunet environments in the terminal
  * `nnUNet_raw_data_base` is where nnU-net V1 stores data for training and testing. You must follow the folder structure provided below.
    * Since we are not training, `imageTr` and `labelsTr` can be empty.
    * `imageTs` contains the T1 scans to be run inference on. Similar to nnU-net V2 in `Step 1` above, images in this folder must have the naming format of `{case_identifier}_0000.nii.gz`.
    * Again for convenience, `nnUNet_raw_data_base/nnUNet_raw_data/Task600_Brainstem/imagesTs` in nnU-net V1 is the same as the `input_folder` for nnU-net V2.
    * For more information on setting up paths, check out: https://github.com/Gitsamshi/nnUNet-1/blob/master/documentation/setting_up_paths.md
```
nnUNet_raw_data_base/nnUNet_raw_data/Task600_Brainstem
├── dataset.json
├── imagesTr
├── imagesTs
│   ├── VS_001_0000.nii.gz
│   ├── VS_002_0000.nii.gz
│   ├── ...
└── labelsTr
```
  * `nnUNet_preprocessed` can be set to a random path and does not mater unless you're training a new model.
  * `RESULTS_FOLDER` must be set to the the folder that contains the extracted 3d_fullres model. The structure should look like below. For more imformation, check out: https://github.com/Gitsamshi/nnUNet-1/tree/master?tab=readme-ov-file#model-training
```
RESULTS_FOLDER/nnUNet/
├── 3d_fullres
│   └── Task600_Brainstem
│       └── nnUNetTrainerV2__nnUNetPlansv2.1
│           ├── fold_0
│           │   ├── model_final_checkpoint.model
│           │   ├── model_final_checkpoint.model.pkl
│           ├── fold_1
│           ├── fold_2
│           ├── fold_3
│           └── fold_4
│           └── plans.pkl
```

### 5. Run the following inference prompt in the terminal
```
nnUNet_predict -i nnUNet1_raw_data_base/nnUNet_raw_data/Task600_Brainstem/imagesTs -o path_to_brainstem_output_folder -tr nnUNetTrainerV2 -m 3d_fullres -p nnUNetPlansv2.1_24GB -t Task600_Brainstem
```
Assuming the input folder looks like the example above, you'll find the automated segmentation brainstem masks in the brainstem_output_folder in the following format if inference was run successfully:
```
 brainstem_output_folder
 ├── VS_001.nii.gz
 ├── VS_002.nii.gz
 ├── VS_003.nii.gz
 ├── ...
```

## Step 3: False Positive Correction
For usage: python vs_false_positive_correction.py -h

Examples of false positive and correction:


<img width="3600" height="3200" alt="VS_fig" src="https://github.com/user-attachments/assets/2be390ef-971e-4d45-b801-6a4452b052b9" />

## Example SLURM Pipeline

For users running this workflow on a high-performance computing (HPC) cluster managed by [SLURM](https://slurm.schedmd.com/), an example batch script is provided in [`example_slurm_pipeline.sh`](example_slurm_pipeline.sh). This script combines the major steps described above into a single GPU job:

1. **Vestibular schwannoma segmentation** using the Kujawa et al. nnU-Net v2 model.
2. **Brainstem segmentation** using the Gesierich et al. nnU-Net v1 model.
3. **False-positive correction** using `vs_false_positive_correction.py`.
4. **Tumor size and diameter calculation** using `calculate_mask_metrics_internal_chord_contour.py`.

The script is intended as a **template rather than a cluster-independent executable**. SLURM configurations, software modules, storage locations, and GPU resource syntax vary between HPC systems. Users should therefore modify the paths and SLURM resource requests before submitting the job.

### 1. Configure the SLURM resources

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

### 2. Configure the working directory, models, and Conda environment

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

### 3. Set up the input directory

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

As described above, each single-channel input image must follow nnU-Net naming conventions:

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

### 4. Specify the locations of the post-processing scripts

The following two lines in `example_slurm_pipeline.sh` must also be changed to the locations of the corresponding scripts on your system:

```bash
python /path/to/vs_false_positive_correction.py \
```

and

```bash
python /path/to/calculate_mask_metrics_internal_chord_contour.py "$POSTPROCESSED_OUTPUT"
```

For example, if this repository has been cloned to `/path/to/VS_segmentation_correction`, these may be changed to:

```bash
python /path/to/VS_segmentation_correction/vs_false_positive_correction.py
```

and

```bash
python /path/to/VS_segmentation_correction/calculate_mask_metrics_internal_chord_contour.py
```

### 5. Configure Conda on your HPC

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

### 6. Cache and temporary files

The example script stores temporary and cache files inside `WORK_DIR` rather than assuming that compute nodes have unrestricted access to the user's home directory. Job-specific cache and temporary directories are created using the SLURM job ID and automatically removed when the job exits.

For HPC systems where compute nodes cannot access the normal home directory, the following lines in the script can also be uncommented:

```bash
export HOME="${WORK_DIR}/home"
mkdir -p "$HOME"
```

This behavior may not be necessary on all systems.

### 7. Submit the pipeline

Once the paths and SLURM settings have been configured, submit the job from the command line:

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
