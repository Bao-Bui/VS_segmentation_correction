# Correction of False Positives in Automated Vestibular Schwannoma (VS) Segmentation
Notes: 
* All the items below were performed on a Windows 10 machine.
* The following procedure only works for contrast-enhanced-T1-weghted scans. Although one can perform tumor segmentation on T2 scans using the model provided in `Step 1`, the brainstem segmentation model used in `Step 2` was trained on only T1 images.
* You're more than welcome to create a Docker container of the following procedures! Please let me know, actually :)

## Step 1: VS Segmentation
The model used was that of Kujawa et al., 2024.
```
Kujawa, A., Dorent, R., Connor, S., Thomson, S., Ivory, M., Vahedi, A., Guilhem, E., Wijethilake, N., Bradford, R., Kitchen, N., Bisdas, S., Ourselin, S., Vercauteren, T., & Shapey, J. (2024).
Deep learning for automatic segmentation of vestibular schwannoma: A retrospective study from multi-center routine MRI. Frontiers in Computational Neuroscience, 18, 1365727.
https://doi.org/10.3389/fncom.2024.1365727

```
Below is a step-by-step instruction on how to implement this model:
1. Download and unzip `MC-RC+SC-GK-models.zip` from the following repository:
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
2. Install nnU-net V2 on your machine
  * Follow the instructions here: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/installation_instructions.md
  * Make sure you download Pytorch first, choosing a Torch version that is compatible with your CUDA version (https://pytorch.org/get-started/previous-versions/). I used torch2.7.1 on CUDA 12.6, which requires python>=3.9.
  * As the developers note, it is strongly recommended that you install nnU-Net V2 in a virtual environment (pip or conda) due to possible interferences with nnU-net V1 used in `Step 2`
4. Set up the nnunet environments in the terminal
  * `nnUNet_raw` can be set to a random path and does not mater unless you're training a new model.
  * `nnUNet_preprocessed` can be set to a random path and does not mater unless you're training a new model.
  * `nnUNet_results` must be set to the location where the trained models are stored. This should be the unzipped folder that contains three trained models (T1, T2, and mixed).
  * For more information, check out: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/setting_up_paths.md
4. Set up the folder containing the T1 scans to be run inference on
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
5. Run the following inference prompt in the terminal
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
1. Download and extract `nnUNet_brainstem.tar.gz` from the following repository:
```
Gesierich, B., & Duering, M. (2024). Deep learning-based brainstem segmentation: nnU-Net model (Version 1.0.2). Zenodo.
https://doi.org/10.5281/ZENODO.13323293
```
This model runs on the framework of nnU-net V1. See Github repository: https://github.com/Gitsamshi/nnUNet-1
2. Install nnU-net V1.7.1 on your machine
  * nnU-net V1 and nnU-net2 can be installed concurrently on a local machine (https://github.com/MIC-DKFZ/nnUNet/releases). However, to avoid dependecy issues, it is recommended that they are built in different virtual environments.
  * Again, make sure you download Pytorch first (see above) in the new virtual environment.
  * Because nnU-net V1.7.1 is deprecated, your python wheel may have trouble resolving dependencies. Furthermore, you will have to make some minor modifications to the source code later (see below). Thus, it is recommended that you clone the Github repository onto your local machine and install it from there. This requires that you have Git installed on your local machine (https://git-scm.com/downloads). Below is an example on how to do this using pip, although conda works as well:
```
pip3 -m venv nnunet1_env
cd nnunet1_env
git clone https://github.com/MIC-DKFZ/nnUNet.git
cd nnUNet
pip install -e .
```
3. Code modifications
  * For torch>=2.6, the default for `torch.load()` is `weights_only = True`. If that is the case, make sure to add `weights_only = False` to the `torch.load()` function in `nnUnet/nnunet/training/model_restore.py`. For more information, see https://docs.pytorch.org/docs/stable/notes/serialization.html#weights-only
  * If you have a Windows machine that uses the `spawn` start method, a lambda function is not pickle-able. On Linux/macOS this never shows up because these OS's use `fork` (which just copies the entire memory without pickling). One way to fix this is to replace the `lambda x: x` function in `nnUNet\nnunet\training\network_training\nnUNetTrainerV2.py` and `nnUNet\nnunet\network_architecture\generic_UNet.py` with `torch.nn.Identity()` which basically does the same thing.
  * Similarly in `nnUNet\nnunet\utilities\nd_softmax.py`, the `softmax_helper = lambda x: F.softmax(x, 1)` should be replaced with the function below. 
```
def softmax_helper(x):
    import torch
    return torch.nn.functional.softmax(x, 1)
```
  * There are more lambda functions throughout the package. Feel free to make changes if needed, but the aforementioned modifications should fix the issues for Windows users.
4. Set up the nnunet environments in the terminal
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

5. Run the following inference prompt in the terminal
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
The logic of the algorithm is as follows:
1. Find the z-coordinate of the most-superior slice that still contains medulla
2. Find all z-coordinates where both medulla and pons are present and take the median thereof. The possible z-coordinate range for the IAC is  [z_medulla_pons_median , z_medulla_max)
3. Label connected components in tumor mask:
   * Keep every component whose z-coordinate range intersects either z_medulla_pons_median or z_medulla_max
   * If ≥1 components satisfy, pick the one whose x-centroid is closest to mid-line
   * Else, pick the component whose lowest slice is nearest to the most-superior slice of the medulla (z_medulla_max)
5.  Save corrected mask

Users have the options of running correction on individual files or in batch-folders. For Python usage:
```
python vs_false_positive_correction_v3.py -h
python vs_false_positive_correction_v3_batch.py -h
```
