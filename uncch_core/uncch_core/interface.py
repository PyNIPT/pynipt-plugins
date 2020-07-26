from pynipt import Processor, InterfaceBuilder
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

    def camri_TSNR(self, input_path, mask_path,
                   regex=None, img_ext='nii.gz', file_idx=None,
                   step_idx=None, sub_code=None, suffix=None):
        from .funcs import tsnr_func
        itf = InterfaceBuilder(self)
        itf.init_step(title='tSNR', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=filter_dict, group_input=False)
        itf.set_var(label='mask', value=mask_path)
        itf.set_output(label='output')
        itf.set_func(tsnr_func)
        itf.set_output_checker(label='output')
        itf.run()

    def camri_ReHo(self, input_path, mask_path, nn_level=3,
                   file_idx=None, regex=None, img_ext='nii.gz',
                   step_idx=None, sub_code=None, suffix=None):
        """
        Args:
            input_path:
            mask_path:
            nn_level:
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            regex(str):         regular express pattern to filter dataset
            img_ext(str):       file extension (default='nii.gz')
            step_idx:
            sub_code:
            suffix:

        Returns:

        """
        from .funcs import reho_func
        itf = InterfaceBuilder(self)
        itf.init_step(title='ReHo', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=filter_dict, group_input=False)
        itf.set_var(label='mask', value=mask_path)
        itf.set_var(label='nn_level', value=nn_level)
        itf.set_output(label='output')
        itf.set_func(reho_func)
        itf.set_output_checker(label='output')
        itf.run()

    def camri_ALFF(self, input_path, mask_path,
                   dt=None, highpass=0.01, lowpass=0.1,
                   file_idx=None, regex=None, img_ext='nii.gz',
                   step_idx=None, sub_code=None, suffix=None):
        """

        Args:
            input_path:
            mask_path:
            dt:
            highpass:
            lowpass:
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            regex(str):         regular express pattern to filter dataset
            img_ext(str):       file extension (default='nii.gz')
            step_idx:
            sub_code:
            suffix:

        Returns:

        """
        from .funcs import alff_func
        itf = InterfaceBuilder(self)
        itf.init_step(title='ALFF', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=filter_dict, group_input=False)
        itf.set_var(label='mask', value=mask_path)
        itf.set_var(label='dt', value=dt)
        itf.set_var(label='highpass', value=highpass)
        itf.set_var(label='lowpass', value=lowpass)
        itf.set_output(label='output')
        itf.set_func(alff_func)
        itf.set_output_checker(label='output')
        itf.run()

    def camri_DVARS(self, input_path, mask_path,
                   file_idx=None, regex=None, img_ext='nii.gz',
                   step_idx=None, sub_code=None, suffix=None):
        """

        Args:
            input_path:
            mask_path:
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            regex(str):         regular express pattern to filter dataset
            img_ext(str):       file extension (default='nii.gz')
            step_idx:
            sub_code:
            suffix:

        Returns:

        """
        from .funcs import dvars_func
        itf = InterfaceBuilder(self)
        itf.init_step(title='DVARS', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=filter_dict, group_input=False)
        itf.set_var(label='mask', value=mask_path)
        itf.set_output(label='output', ext='tsv')
        itf.set_func(dvars_func)
        itf.set_output_checker(label='output')
        itf.run()

    def camri_FramewiseDisplacement(self, input_path, mean_radius=None,
                                    file_idx=None, regex=None, img_ext='1D',
                                    step_idx=None, sub_code=None, suffix=None):
        """

        Args:
            input_path:
            mean_radius:
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            regex(str):         regular express pattern to filter dataset
            img_ext(str):       file extension (default='1D')
            step_idx:
            sub_code:
            suffix:

        Returns:

        """
        from .funcs import fd_func
        itf = InterfaceBuilder(self)
        itf.init_step(title='FramewiseDisplacement', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=filter_dict, group_input=False)
        itf.set_var(label='mean_radius', value=mean_radius)
        itf.set_output(label='output', ext='tsv')
        itf.set_func(fd_func)
        itf.set_output_checker(label='output')
        itf.run()

    def camri_Standardize(self, input_path, mask_path,
                          regex=None, img_ext='nii.gz', file_idx=None,
                          step_idx=None, sub_code=None, suffix=None):
        """ Standardize data

        Args:
            input_path(str):    datatype or stepcode of input data
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            regex(str):         regular express pattern to filter dataset
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        from .funcs import standardize_func
        itf = InterfaceBuilder(self)
        itf.init_step(title='StandardizeSignal', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=filter_dict, group_input=False)
        itf.set_var(label='mask', value=mask_path)
        itf.set_output(label='output')
        itf.set_func(standardize_func)
        itf.set_output_checker(label='output')
        itf.run()

    def camri_BrainMasking(self, input_path, file_idx=None, regex=None, img_ext='nii.gz',
                           step_idx=None, sub_code=None, suffix=None):
        """ Estimate brain mask using 2D-UNET,

        Args:
            input_path(str):    datatype or stepcode of input data
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            regex(str):         regular express pattern to filter dataset
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
                                 file_idx=None, regex=None, img_ext='nii.gz',
                                 fwhm=None, highpass=None, lowpass=None,
                                 ort=None, ort_regex=None, ort_ext=None,
                                 step_idx=None, sub_code=None, suffix=None):
        """
        Args:
            input_path:
            dt: sample time in second
            mask_path: mask path
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            regex(str):         regular express pattern to filter dataset
            img_ext(str):       file extension (default='nii.gz')
            fwhm:
            highpass:
            lowpass:
            ort:
            ort_regex:
            step_idx:
            sub_code:
            suffix:
        """
        from .funcs import nuisance_regression_func
        itf = InterfaceBuilder(self)
        itf.init_step(title='NuisanceRegression', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=filter_dict, group_input=False)
        itf.set_var(label='mask', value=mask_path)
        itf.set_var(label='fwhm', value=fwhm)
        itf.set_var(label='highpass', value=highpass)
        itf.set_var(label='lowpass', value=lowpass)
        itf.set_var(label='dt', value=dt)
        itf.set_var(label='bp_order', value=5)
        if ort:
            if not ort_regex:
                raise InvalidApproach('Regex pattern must provided for ort option.')
            if not ort_ext:
                raise InvalidApproach('Extension hint of ort must be provided.')
            itf.set_input(label='ort', input_path=ort,
                          filter_dict=dict(regex=ort_regex, ext=ort_ext))
        else:
            itf.set_var(label='ort', value=ort)
        itf.set_var(label='pn_order', value=3)
        itf.set_func(nuisance_regression_func)
        itf.set_output(label='output')
        itf.set_output_checker(label='output')
        itf.run()

    def camri_ModeNormalization(self, input_path, mask_path=None, mode=1000,
                                file_idx=None, regex=None, img_ext='nii.gz',
                                step_idx=None, sub_code=None, suffix=None):
        """
        Args:
            input_path(str):    datatype or stepcode of input data
            mask_path(str):      mask
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            regex(str):         regular express pattern to filter dataset
            img_ext(str):       file extension (default='nii.gz')
            mode:               mode
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        from .funcs import modenorm_func
        itf = InterfaceBuilder(self)
        itf.init_step(title='ModeNormalization', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=filter_dict, group_input=False)
        itf.set_var(label='mask', value=mask_path)
        itf.set_var(label='mode', value=mode)
        itf.set_func(modenorm_func)
        itf.set_output(label='output')
        itf.set_output_checker(label='output')
        itf.run()

    def camri_Periodogram(self, input_path, mask_path=None, dt=None, nfft=None,
                          file_idx=None, regex=None, img_ext='nii.gz',
                          step_idx=None, sub_code=None, suffix=None):
        """
        Args:
            input_path(str):    datatype or stepcode of input data
            mask_path(str):      mask
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            regex(str):         regular express pattern to filter dataset
            img_ext(str):       file extension (default='nii.gz')
            mode:               mode
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        from .funcs import periodogram_func
        itf = InterfaceBuilder(self)
        itf.init_step(title='Periodogram', mode='processing', type='python',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=filter_dict, group_input=False)
        itf.set_var(label='mask', value=mask_path)
        itf.set_var(label='dt', value=dt)
        itf.set_var(label='nfft', value=nfft)
        itf.set_func(periodogram_func)
        itf.set_output(label='output')
        itf.set_output_checker(label='output')
        itf.run()
