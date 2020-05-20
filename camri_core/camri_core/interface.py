from pynipt import Processor, InterfaceBuilder
from .funcs import modenorm_func, nuisance_filtering_func
from shleeh.errors import *
import sys


class Interface(Processor):
    """command line interface example
    """

    def __init__(self, *args, **kwargs):
        super(Interface, self).__init__(*args, **kwargs)

    # TODO: Preprocessing tools
    # def camri_MotionCorrection(self):
    #     pass
    #
    # def camri_SpatialNormalizationSyN(self):
    #     pass
    #
    # def camri_ApplySpatialNorm(self):
    #     pass

    # TODO: QC tools
    # def camri_TSNR(self):
    #     pass
    #
    # def camri_ReHo(self):
    #     pass
    #
    # def camri_ALFF(self):
    #     pass
    #
    # def camri_DVARS(self):
    #     pass

    def camri_BrainMasking(self, input_path, file_idx=None, regex=None, img_ext='nii.gz',
                           step_idx=None, sub_code=None, suffix=None):
        """ Estimate brain mask using 2D-UNET,

        Args:
            input_path(str):    datatype or stepcode of input data
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            regex:
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self, n_threads=1)
        itf.init_step(title='BrainMaskEstimate', mode='masking',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, group_input=False, idx=file_idx,
                      filter_dict=filter_dict)
        itf.set_output(label='mask', suffix='_mask')
        itf.set_output(label='copy')
        itf.set_cmd("rbm *[input] *[mask]")
        if sys.platform == 'win32':
            itf.set_cmd("copy *[input] *[copy]")
        else:
            itf.set_cmd("cp *[input] *[copy]")
        itf.set_output_checker(label='mask')
        itf.run()

    def camri_NuisanceRegression(self, input_path, dt, mask_path=None,
                                 regex=None, img_ext='nii.gz',
                                 fwhm=None, bandcut=None,
                                 ort=None, ort_regex=None, ort_ext=None,
                                 step_idx=None, sub_code=None, suffix=None):
        """
        Args:
            input_path:
            dt:
            mask_path:
            regex:
            img_ext:
            fwhm:
            bandcut:
            ort:
            ort_regex:
            step_idx:
            sub_code:
            suffix:
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='NuisanceRegression', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path,
                      filter_dict=filter_dict, group_input=False)
        if mask_path is not None:
            itf.set_var(label='mask', value=mask_path)
        if fwhm is not None:
            itf.set_var(label='fwhm', value=fwhm)
        if bandcut is not None:
            itf.set_var(label='bandcut', value=bandcut)
        if ort is not None:
            if ort_regex is None:
                raise InvalidApproach('Regex pattern must provided for ort option.')
            if ort_ext is None:
                raise InvalidApproach('Extension hint of ort must be provided.')
            itf.set_static_input(label='ort', input_path=ort, idx=0,
                                 filter_dict=dict(regex=ort_regex, ext=ort_ext))
        itf.set_var(label='dt', value=dt)
        itf.set_var(label='bp_order', value=5)
        itf.set_var(label='pn_order', value=3)
        itf.set_func(nuisance_filtering_func)
        itf.set_output(label='output')
        itf.set_output_checker(label='output')
        itf.run()

    def camri_ModeNormalization(self, input_path, mask_path=None, mode=1000,
                                regex=None, img_ext='nii.gz',
                                step_idx=None, sub_code=None, suffix=None):
        """
        Args:
            input_path(str):    datatype or stepcode of input data
            mask_path(str):      mask
            regex:
            mode:               mode
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='ModeNormalization', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path,
                      filter_dict=filter_dict, group_input=False)
        itf.set_var(label='mask', value=mask_path)
        itf.set_var(label='mode', value=mode)
        itf.set_func(modenorm_func)
        itf.set_output(label='output')
        itf.set_output_checker(label='output')
        itf.run()
