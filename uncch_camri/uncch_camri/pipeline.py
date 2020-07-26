from pynipt import PipelineBuilder


class UNCCH_CAMRI(PipelineBuilder):
    def __init__(self, interface,
                 # User defined arguments
                 # -- start -- #

                 # CorePreprocessing:
                 anat='anat', func='func',
                 tr=2, tpattern='altplus',
                 template_path=None, aniso=False,

                 # CBV-fMRI specific parameters
                 cbv_regex=None, cbv_scantime=None,

                 # GLM analysis
                 hrf_model=None, hrf_parameters=None, stim_onsets=None,
                 step_idx=None, step_tag=None,

                 # RSFC
                 regex=None,
                 fwhm=0.5, mask_path=None,
                 nn=3,
                 highpass=0.01, lowpass=0.1,

                 # T-test
                 output_filename=None, groupa=None, groupb=None, groupa_regex=None, groupb_regex=None, clustsim=None,

                 # MVM

                 # --  end  -- #
                 ):
        """
        Standard fMRI pipeline package for the University of North Carolina at Chapel Hill,
        to use for the data analysis services in Center of Animal MRI (CAMRI)
        Author  : SungHo Lee(shlee@unc.edu)
        Revised :
            ver.1: Dec.11st.2017
            ver.2: Mar.7th.2019
        Keyword Args: - listed based on each steps
            - 01_MaskPreparation
            anat(str):          datatype for anatomical image (default='anat')
            func(str):          datatype for functional image (default='func')
            tr(int):            the repetition time of EPI data
            tpattern(str):      slice order of image
                alt+z = altplus   = alternating in the plus direction
                alt+z2            = alternating, starting at slice #1 instead of #0
                alt-z = altminus  = alternating in the minus direction
                alt-z2            = alternating, starting at slice #nz-2 instead of #nz-1
                seq+z = seqplus   = sequential in the plus direction
                seq-z = seqminus  = sequential in the minus direction
            # Optional for CBV image
            cbv_regex(str):     regular expression pattern of filename to select dataset.
                                this option can be used when cbv data acquired instead of BOLD,
                                because of the negative contrast effect of MION, cbv image is hard to
                                register with regular contrasted image. by providing this option to choose
                                file's regex pattern of MION infusion data, it will creates average image using
                                first 20 frames and last 20 frames to generate BOLD and CBV average images.
            cbv_scantime(int):  total scantime for MION infusion image in second.

            - 02_CorePreprocessing
            template_path(str): absolute path of brain template image (default=None)
            aniso(bool):        True if voxel is anisotropic (default=False)
                                This option is for the image has truncated brain with thicker slice thickness
                                and it uses afni's linear registration for normalization instead ants's non-linear
                                registration tool, SyN.

            - 03_GeneralLinearModeling
            regex(str):             Regular express pattern of filename to select dataset
            mask_path(str):         path of brain mask image
            fwhm(int or float):     full width half maximum value for smoothing
            hrf_model(str):         Hemodynamic Response Function (HRF) according to the 3dDeconvolve command in Afni
            hrf_parameters(list):   parameter values for the HRF
            stim_onset(list):       stimulation onset times
            step_idx(idx):          step_index to classify the step with other when apply multiple
            step_tag(str):          suffix tag to classify the step with other when apply multiple

            - 04_RSFC
            step_idx(idx):          step_index to classify the step with other when apply multiple
            step_tag(str):          suffix tag to classify the step with other when apply multiple
            highpass(float):
            lowpass(float):

            - 05_TTest
            output_filename(str):   output filename of 2nd level analysis
            groupa(str):            datatype or stepcode of input data of group A
            groupb(str):            datatype or stepcode of input data of group B
            groupa_regex(str):      regular express pattern to filter group A
            groupb_regex(str):      regular express pattern to filter group B
            clustsim(bool):         use Clustsim option if True
            step_idx(idx):          step_index to classify the step with other when apply multiple
            step_tag(str):          suffix tag to classify the step with other when apply multiple

            - 06_MVM
        """
        super(UNCCH_CAMRI, self).__init__(interface)
        # User defined attributes for storing arguments
        # -- start -- #
        # 01_MaskPreparation
        self.anat = anat
        self.func = func
        self.tr = tr
        self.tpattern = tpattern
        self.cbv_regex = cbv_regex
        self.cbv_scantime = cbv_scantime

        # 02_CorePreprocessing
        self.template_path = template_path
        self.aniso = aniso

        # 03_GeneralLinearModeling
        self.regex = regex
        self.mask_path = mask_path
        self.fwhm = fwhm
        self.hrf_model = hrf_model
        self.hrf_parameters = hrf_parameters
        self.stim_onsets = stim_onsets
        self.step_idx = step_idx
        self.step_tag = step_tag

        # 04_RSFC_SignalCleaning
        # self.fwhm = fwhm
        # self.tr = tr
        # self.regex = regex
        self.highpass = highpass
        self.lowpass = lowpass
        self.nn = nn

        # 05_TTest
        self.output_filename = output_filename
        self.groupa = groupa
        self.groupa_regex = groupa_regex
        self.groupb = groupb
        self.groupb_regex = groupb_regex
        self.clustsim = clustsim

        # 06_MVM

        # --  end  -- #

    def pipe_01_MaskPreparation(self):
        """
        The dataset will be first slice timing corrected, then it will generate the average intensity map
        of functional data for mask estimation. In the end of this pipeline, brain mask image file
        will be generated in the masking path with '_mask' suffix.
        """
        # Series of user defined interface commands to executed for the pipeline
        # -- start -- #
        self.interface.afni_SliceTimingCorrection(input_path=self.func,
                                                  tr=self.tr, tpattern=self.tpattern,
                                                  step_idx=1, sub_code=0)
        if self.cbv_regex is not None:
            if self.cbv_scantime is None:
                raise Exception('cbv_scantime parameter must be provided.')
            else:
                cbv_ntr = int(self.cbv_scantime / self.tr)-1
            self.interface.afni_MotionCorrection(input_path='010', regex=self.cbv_regex, file_idx=0,
                                                 fourier=True, verbose=True, mparam=False,
                                                 step_idx=2, sub_code='A', suffix='base')
            self.interface.afni_MeanImageCalc(input_path='02A', file_idx=0, range=[0, 19],
                                              step_idx=1, sub_code='A', suffix='bold')
            self.interface.afni_MeanImageCalc(input_path='02A', file_idx=0, range=[cbv_ntr-20, cbv_ntr],
                                              step_idx=1, sub_code='D', suffix='cbv')
        else:
            self.interface.afni_MotionCorrection(input_path='010', file_idx=0,
                                                 fourier=True, verbose=True, mparam=False,
                                                 step_idx=2, sub_code='A', suffix='base')
            self.interface.afni_MeanImageCalc(input_path='010', file_idx=0,
                                              step_idx=1, sub_code='A')
        self.interface.camri_BrainMasking(input_path='01A', file_idx=0,
                                          step_idx=1, sub_code='B', suffix=self.func)
        if self.anat is not None:
            self.interface.camri_BrainMasking(input_path=self.anat, file_idx=0,
                                              step_idx=1, sub_code='C', suffix=self.anat)

    def pipe_02_CorePreprocessing(self):
        """
        Prior to run this pipeline, template_path argument need to be provided.
        All the dataset will be motion corrected, and skull stripping will be applied.
        If the anatomical data are inputted, then functional data will be co-registered into
        anatomical space using affine registration.
        Finally, the functional data will be normalized into template space using ANTs SyN non-linear
        registration.
        """
        # Series of user defined interface commands to executed for the pipeline
        # -- start -- #

        # Check if the brain template image is exist in given path
        if self.template_path is None:
            raise Exception('No brain template image is provided.')
        else:
            if not self.interface.msi.path.exists(self.template_path):
                raise Exception('No brain template image found on given path.')

        if self.cbv_regex is not None:
            self.interface.afni_MotionCorrection(input_path='010', base='01D', regex=fr'^(?!{self.cbv_regex})',
                                                 fourier=True, verbose=True, mparam=True,
                                                 step_idx=2, sub_code=0, suffix=self.func)
        else:
            self.interface.afni_MotionCorrection(input_path='010', base='01A',
                                                 fourier=True, verbose=True, mparam=True,
                                                 step_idx=2, sub_code=0, suffix=self.func)

        self.interface.afni_SkullStripping(input_path='01A', mask_path='01B', file_idx=0,
                                           step_idx=3, sub_code='A', suffix=f'mean{self.func}')
        if self.anat is not None:
            # if anatomy dataset is provided, then co-registration process will be applied
            self.interface.afni_SkullStripping(input_path=self.anat, mask_path='01C',
                                               step_idx=3, sub_code='B', suffix=self.anat)
            self.interface.ants_N4BiasFieldCorrection(input_path='03A', file_idx=0,
                                                      step_idx=3, sub_code='C',
                                                      suffix=f'mean{self.func}')
            self.interface.ants_N4BiasFieldCorrection(input_path='03B', file_idx=0,
                                                      step_idx=3, sub_code='D',
                                                      suffix=self.anat)
            self.interface.afni_Coregistration(input_path='03C', ref_path='03D', file_idx=0,
                                               step_idx=3, sub_code='E',
                                               suffix=f'mean{self.func}')
            if self.aniso is True:
                self.interface.afni_SpatialNorm(input_path='03D', ref_path=self.template_path,
                                                step_idx=4, sub_code='A',
                                                suffix=self.anat)
                self.interface.afni_ApplySpatialNorm(input_path='03A', ref_path='04A',
                                                     step_idx=4, sub_code='B',
                                                     suffix=f'mean{self.func}')
            else:
                self.interface.ants_SpatialNorm(input_path='03D', ref_path=self.template_path,
                                                step_idx=4, sub_code='A',
                                                suffix=self.anat)
                self.interface.ants_ApplySpatialNorm(input_path='03A', ref_path='04A',
                                                     step_idx=4, sub_code='B',
                                                     suffix=f'mean{self.func}')

            self.interface.afni_SkullStripping(input_path='020', mask_path='01B',
                                               step_idx=3, sub_code='F',
                                               suffix=self.func)
            self.interface.afni_ApplyTransform(input_path='03F', ref_path='03E',
                                               step_idx=3, sub_code=0,
                                               suffix=self.func)
        else:
            self.interface.afni_SkullStripping(input_path='020', mask_path='01B',
                                               step_idx=3, sub_code=0,
                                               suffix=self.func)
            self.interface.ants_SpatialNorm(input_path='03A', ref_path=self.template_path,
                                            step_idx=4, sub_code='A',
                                            suffix=self.anat)

        if self.aniso is True:
            self.interface.afni_ApplySpatialNorm(input_path='030', ref_path='04A',
                                                 step_idx=4, sub_code=0,
                                                 suffix=self.func)
        else:
            self.interface.ants_ApplySpatialNorm(input_path='030', ref_path='04A',
                                                 step_idx=4, sub_code=0,
                                                 suffix=self.func)
        # --  end  -- #

    def pipe_03_GeneralLinearModeling(self):
        """
        The normalized data will be scaled to have mean value of 100 for each voxel followed by the spacial smoothing
        at given FWHM. Finally, GLM will be performed to get subject level task activity map
        """
        # Series of user defined interface commands to executed for the pipeline
        # -- start -- #
        self.interface.afni_Scailing(input_path='040', mask_path=self.mask_path,
                                     mean=100, max=200, step_idx=self.step_idx, sub_code='A',
                                     suffix=self.step_tag)
        self.interface.afni_BlurToFWHM(input_path=f'{str(self.step_idx).zfill(2)}A',
                                       fwhm=self.fwhm,
                                       step_idx=self.step_idx, sub_code='B', suffix=self.step_tag)
        self.interface.afni_Deconvolution(input_path=f'{str(self.step_idx).zfill(2)}B',
                                          mask_path=self.mask_path,
                                          regex=self.regex,
                                          onset_time=self.stim_onsets, model=self.hrf_model,
                                          parameters=self.hrf_parameters,
                                          step_idx=self.step_idx, sub_code=0, suffix=self.step_tag)
        # reset step_idx and step_tag
        self.step_idx = None
        self.step_tag = None
        # --  end  -- #

    def pipe_04_RSFC(self):
        """
        First step, QC - DVARS before signal filtering (HP only), TSNR, and FD
        Second step, Filtering and QC - DVARS after signal filtering, TSNR, and FD
        ALFF, ReHo, seed-based Connectivity, and pair-wise ROI-based connectivity
        """
        # hp_suffix = f'{self.step_tag}_HP'
        # bp_suffix = f'{self.step_tag}_HP'

        # self.interface.camri_DVARS(input_path='XXX, mask_path=self.mask_path,
        #                    file_idx=None, regex=None, img_ext='nii.gz',
        #                    step_idx=None, sub_code=None, suffix=None))
        # self.interface.camri_FramewiseDisplacement(input_path='XXX', mean_radius=None,
        #                                            file_idx=None, regex=None, img_ext='1D',
        #                                            step_idx=None, sub_code=None, suffix=None)
        # self.interface.camri_NuisanceRegression(input_path='040', dt=self.tr, mask_path=self.mask_path,
        #                                         regex=self.regex,
        #                                         fwhm=self.fwhm, highpass=self.highpass, lowpass=self.lowpass,
        #                                         ort='020', ort_regex='.*', ort_ext='1D',
        #                                         step_idx=self.step_idx, sub_code='B', suffix=bp_suffix)

        # input_path = f'{str(self.step_idx).zfill(2)}A'
        # self.interface.camri_ModeNormalization(input_path=input_path, mask_path=self.mask_path,
        #                                        regex=self.regex, mode=1000,
        #                                        step_idx=self.step_idx, sub_code='C', suffix=hp_suffix)
        # self.interface.camri_Standardize(input_path=input_path, mask_path=self.mask_path, regex=self.regex,
        #                                  step_idx=self.step_idx, sub_code='E', suffix=bp_suffix)
        #
        # input_path = f'{str(self.step_idx).zfill(2)}C'
        # self.interface.camri_TSNR(input_path=input_path, mask_path=self.mask_path, regex=self.regex,
        #                           step_idx=self.step_idx, sub_code='F', suffix=self.step_tag)
        # self.interface.camri_Periodogram()
        # self.interface.camri_ALFF(input_path=input_path, mask_path=self.mask_path, regex=self.regex,
        #                           highhass=self.highpass, lowpass=self.lowpass, dt=self.tr,
        #                           step_idx=self.step_idx, sub_code='G', suffix=self.step_tag)
        #
        # input_path = f'{str(self.step_idx).zfill(2)}D'
        # self.interface.camri_ReHo(input_path=input_path, mask_path=self.mask_path, nn_level=self.nn, regex=self.regex,
        #                           step_idx=self.step_idx, sub_code='F', suffix=self.step_tag)
        self.step_idx = None
        self.step_tag = None

    def pipe_05_2ndLevel_TTest(self):
        """
        3dttest++ is used to perform ttest. With Clustsim option, clustsim table will be generated and integrated
        into the result file.
        """
        # Series of user defined interface commands to executed for the pipeline
        # -- start -- #
        self.interface.afni_TTest(output_filename=self.output_filename, clustsim=self.clustsim,
                                  input_a=self.groupa, regex_a=self.groupa_regex, data_idx_a=1,
                                  input_b=self.groupb, regex_b=self.groupb_regex, data_idx_b=1,
                                  mask_path=self.mask_path,
                                  step_idx=self.step_idx, sub_code=None, suffix=self.step_tag)
        # reset step_tag
        self.step_idx = None
        self.step_tag = None
        # --  end  -- #

    # def pipe_06_MVM(self):
    #     """
    #     """
    #     # Series of user defined interface commands to executed for the pipeline
    #     # -- start -- #
    #
    #     # reset step_tag
    #     self.step_idx = None
    #     self.step_tag = None
    #     # --  end  -- #