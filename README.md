# Correction of False Positives in Automated Vestibular Schwannoma (VS) Segmentation
`Note:` All the items below were performed on a Windows 10 machine. The following procedure only works for contrast-enhanced-T1-weghted scans because although one can perform tumor segmentation on T2 scans using the model provided in `Step 1`, the brainstem segmentation model used in `Step 2` was trained on only T1 images.

## Step 1. VS Segmentation
The model used was that of Kujawa et al., 2024.
```
citation
```
Below is a step-by-step instruction on how to implement this model:
1. Download and unzip `MC-RC+SC-GK-models.zip` from the following repository:
```
Aaron Kujawa, Dorent, R., Wijethilake, N., Connor, S., Thomson, S., Ivory, M., Bradford, R., Kitchen, N., Bisdas, S., Ourselin, S., Vercauteren, T., & Shapey, J. (2023).
Deep Learning for Automatic Segmentation of Vestibular Schwannoma: A Retrospective Study from Multi-Centre Routine MRI -- Deep learning models. Zenodo. https://doi.org/10.5281/zenodo.10363647
```
This model runs on the framework of nnU-net V2, whose Github repository and original paper are as follows
```
Original Paper: Isensee, F., Jaeger, P. F., Kohl, S. A., Petersen, J., & Maier-Hein, K. H. (2021).
nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation. Nature methods, 18(2), 203-211.

Github: https://github.com/MIC-DKFZ/nnUNet
```
2. Set up the nnunet environments in the terminal
  * `nnUNet_raw` can be set to a random path and does not mater unless you're training a new model.
  * `nnUNet_preprocessed` can be set to a random path and does not mater unless you're training a new model.
  * `nnUNet_results` must be set to the location where the trained models are stored. This should be the unzipped folder that contains three trained models (T1, T2, and mixed).
  * For more information, check out: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/setting_up_paths.md
3. Set up the folder containing the T1 scans to be run inference on
  * Although nnU-net V2 supports many file formats, it is conventional to run inferences on NIfTI files. NIfTI conversion from DICOM files can be done using `3DSlicer` or `dcm2nii`.
  * For models that were trained on only one imaging modality (the one used below), imaging files in the `input_folder` must follow the naming format of {case_identifier}_0000.nii.gz file. For example:
```
 input_folder
 ├── VS_001_0000.nii.gz
 ├── VS_002_0000.nii.gz
 ├── VS_003_0000.nii.gz
```
  * For the MCRC-SCGK T1 3d_fullres model that will be used below, _0000 indicates to the model that the images in the `input_folder` are T1 images, as specified by the `dataset.json` file in the trained model.
  * For more information on the formatting of `input_folder`, check out: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format_inference.md
  * For more information on modality indicators (or channel names as nnU-net V2 calls it), check out: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/dataset_format.md
4. Run the following inference prompt in the terminal
```
nnUNetv2_predict -d Dataset920_VSMCRCSCGKT1 -i path_to_input_folder -o path_to_output_folder -f  0 1 2 3 4 -tr nnUNetTrainer -c 3d_fullres -p nnUNetPlan
```
* Assuming the input folder looks like the example above, you'll find the automated segmentation tumor masks in the output_folder in the following format if the inference was run successfully:
```
 output_folder
 ├── VS_001.nii.gz
 ├── VS_002.nii.gz
 ├── VS_003.nii.gz
```
