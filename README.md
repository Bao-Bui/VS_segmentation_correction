# Correction of False Positives in Automated Vestibular Schwannoma (VS) Segmentation
`Note:` All the items below were performed on a Windows 10 machine.

## 1. VS Segmentation
The model used was that of Kujawa et al., 2024.
```
citation
```
Below is a step-by-step instruction on how to implement this model:
1. Download and unzip `MC-RC+SC-GK-models.zip` from the following repository:
```
Aaron Kujawa, Dorent, R., Wijethilake, N., Connor, S., Thomson, S., Ivory, M., Bradford, R., Kitchen, N., Bisdas, S., Ourselin, S., Vercauteren, T., & Shapey, J. (2023). Deep Learning for Automatic Segmentation of Vestibular Schwannoma: A Retrospective Study from Multi-Centre Routine MRI -- Deep learning models. Zenodo. https://doi.org/10.5281/zenodo.10363647
```
This model runs on the framework of nnU-netv2, whose Github repository and original paper are as follows
```
Original Paper: Isensee, F., Jaeger, P. F., Kohl, S. A., Petersen, J., & Maier-Hein, K. H. (2021). nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation. Nature methods, 18(2), 203-211.
Github: https://github.com/MIC-DKFZ/nnUNet
```
2. Set up the nnunet environments in the terminal
* 
   
