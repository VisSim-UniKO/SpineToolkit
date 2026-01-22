# SpineToolkit

This extension includes modules for the analysis and reconstruction of 3D spine models.

## LumbarSpineCreator

Lumbar Spine Creator generates an artificial model of the lumbar spine, including vertebrae L1-L5 and the sacrum. The user can set the lumbar lordosis angle and a minimum and maximum value for the intervertebral disc height. Individual FSU parameters (angles and IVD height) are calculated based on a distribution, which depends on the selected subject position. Optionally, the respective parameters can be set for each FSU individually. The output includes the models of L1, L2, L3, L4, L5, SA, aligned as a coherent artificial lumbar spine, along with a table of measurements about the lumbar spine.

<img src="https://github.com/user-attachments/assets/8f563004-0a75-40af-bec3-da1feb6e0ecc" width=60% height=60%>

#### Publication:
L. Blomenkamp, I. Kramer, S. Bauer and D. Paulus, "Efficient Generation of 3D Lumbar Spine Models: An Anatomy-Driven Approach with Limited Input Parameters," 2023 International Symposium on Image and Signal Processing and Analysis (ISPA), Rome, Italy, 2023, pp. 1-6, doi: 10.1109/ISPA58351.2023.10278898.


## Lumbar Spine Reconstruction

The LumbarSpineReconstruction module registrates a set of artificial sawbone models to custom spine models (L1-L5). The goal is to align sawbones with the provided vertebra models, which consist of only the vertebral bodies. In the registration process, the position, orientation and size of the sawbones are adjusted to match the custom spine.

<img src="https://github.com/user-attachments/assets/5e5ff24d-9f53-458d-ad91-3a72c7ce18b1" width=60% height=60%>

#### Publication:
L. Blomenkamp, I. Kramer, S. Bauer, K. Weirauch and D. Paulus, "Reconstruction of 3D lumbar spine models from incomplete segmentations using landmark detection," 2024 46th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC), Orlando, FL, USA, 2024, pp. 1-6, doi: 10.1109/EMBC53108.2024.10782468.


## Spine Shape Segmentation

The ShapeSegmentation module segments vertebrae into their components: The vertebral body, laminae, transverse processes, articular processes and spinous process. The segment labels are saved in the models ScalarArray "Labels".

<img src="https://github.com/user-attachments/assets/4f42131d-ec0f-4c11-bb2a-ceb906cba17d" width=60% height=60%>


#### Publication:
L. Blomenkamp, I. Kramer, S. Bauer and D. Paulus, "A Novel Approach for Shape Segmentation of Vertebrae: Decomposition into Anatomical Regions Using 3D Skeletonization," 2025 47th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC), Copenhagen, Denmark, 2025, pp. 1-6, doi: 10.1109/EMBC58623.2025.11254383.


## Ligament Landmark Detection

The LigamentLandmarkDetection module implements a novel approach for detecting spinal ligament landmarks. The method first performs shape-based segmentation of 3D vertebrae and subsequently applies domain-specific rules to identify different types of attachment points.

<img src=<img width="2880" height="1704" alt="Slicer_ligs" src="https://github.com/user-attachments/assets/5bff0f50-ea62-4b4c-a332-da212e4f0d28" />
 width=60% height=60%>

#### Publication:
Paper accepted for publication
