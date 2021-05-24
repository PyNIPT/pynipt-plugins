from pynipt import Processor, InterfaceBuilder
from shleeh.errors import *
import sys


class Interface(Processor):
    """command line interface example
    """

    def __init__(self, *args, **kwargs):
        super(Interface, self).__init__(*args, **kwargs)

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
