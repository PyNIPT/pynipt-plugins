[![DOI](https://zenodo.org/badge/260246568.svg)](https://zenodo.org/badge/latestdoi/260246568)
# PyNIPT-PlugIns

#### The collection of Pipeline PlugIns that developed to use in CAMRI at University of North Carolina.

### Description
- **UNCCH_CAMRI**: 
  - legacy version of the pipeline
  - dependency on ANTs, AFNI, and CAMRI_CORE plugin
  - core fMRI preprocessing pipeline
  - task-based fMRI analysis pipeline
  - 2nd level statistics using 3dMVM or 3dttest++ of AFNI
  
- **CAMRI_CORE**: 
  - naive python pipeline
  - migrating to use pure python libraries to achive cross platform
  - dipy, SimpleITK for registration
  - nilearn for preprocessing
  - ECT, slfmri (personal library)
