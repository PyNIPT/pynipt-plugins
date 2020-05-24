from slfmri.lib.volume import modenorm, standardize
from slfmri.lib.timeseries import nuisance_regression, bandpass
from slfmri.lib.utils import get_funcobj, apply_funcobj
from slfmri.lib.io import load
from slfmri.lib.volume.man import nib2sitk, sitk2nib, gaussian_smoothing
from shleeh.utils import user_warning
from shleeh.errors import *
from sklearn.linear_model import BayesianRidge
import nibabel as nib
import numpy as np
import sys
from typing import List, Optional, Union, IO


def standardization_func(input: str, output: str, mask: Optional[str] = None,
                         stdout: Optional[IO] = None,
                         stderr: Optional[IO] = None
                         ):
    """ Signal standardization
    Args:
        input: file path of input data (.nii or .nii.gz)
        output: file path for output destination (.nii or .nii.gz)
        mask: file path of mask image (.nii or .nii.gz)
        stdout: IO stream for message
        stderr: IO stream for error message
    Returns:
        0 if success else 1
    """
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    stdout.write('[UNCCH_CAMRI] Standardization:\n')
    try:
        img = nib.load(input)
        func_img = np.asarray(img.dataobj)
        stdout.write(f'  Input path  : {input}\n')
        if mask is not None:
            stdout.write(f'  Mask_path   : {mask}\n')
            mask_img = np.asarray(nib.load(mask).dataobj)
        else:
            stdout.write('  No Mask file was provided.\n')
            user_warning('Performing standardization without a mask can lead to inaccurate results.'
                         'No Mask option only suggested when the image had bin skull stripped,'
                         'which voxels located at outside of the brain set to 0.')
            mask_img = None
        normed_img = standardize(func_img, mask_img, io_handler=stdout)
        stdout.write(f'  Output path : {output}\n')
        normed_nii = nib.Nifti1Image(normed_img, img.affine)
        normed_nii._header = img.header.copy()
        normed_nii.to_filename(output)
        stdout.write('Done...\n'.format(output))
    except:
        import traceback
        stderr.write('[ERROR] Failed.\n')
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    return 0


def modenorm_func(input: str, output: str, mask: Optional[str] = None,
                  mode: int = 1000,
                  stdout: Optional[IO] = None,
                  stderr: Optional[IO] = None):
    """ FSL's Mode normalization python implementation.
    Args:
        input: file path of input data (.nii or .nii.gz)
        output: file path for output destination (.nii or .nii.gz)
        mask: file path of mask image (.nii or .nii.gz)
        mode: target value for data average
        stdout: IO stream for message
        stderr: IO stream for error message
    Returns:
        0 if success else 1
    """
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    stdout.write('[UNCCH_CAMRI] Mode Normalization:\n')

    try:
        img = nib.load(input)
        func_img = np.asarray(img.dataobj)
        stdout.write(f'  Input path  : {input}\n')
        if mask is not None:
            stdout.write(f'  Mask_path   : {mask}\n')
            mask_img = np.asarray(nib.load(mask).dataobj)
        else:
            stdout.write('  No Mask file was provided.\n')
            user_warning('Performing mode normalization without a mask can lead to inaccurate results.'
                         'No Mask option only suggested when the image had bin skull stripped,'
                         'which voxels located at outside of the brain set to 0.')
            mask_img = None
        stdout.write(f'  Target mode value: {mode}\n')
        normed_img = modenorm(func_img, mask_img, mode, io_handler=stdout)
        stdout.write(f'  Output path : {output}\n')
        normed_nii = nib.Nifti1Image(normed_img, img.affine)
        normed_nii._header = img.header.copy()
        normed_nii.to_filename(output)
        stdout.write('Done...\n'.format(output))
    except:
        import traceback
        stderr.write('[ERROR] Failed.\n')
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    return 0


def nuisance_filtering_func(input: str, output: str, mask: Optional[str] = None,
                            bandcut: Optional[Union[List[float], float]] = None,
                            fwhm: Optional[float] = None,
                            dt: Optional[Union[int, float]] = None,
                            bp_order: Optional[int] = 5,
                            ort: Optional[str] = None,
                            pn_order: Optional[int] = 3,
                            stdout: Optional[IO] = None,
                            stderr: Optional[IO] = None):
    """ Python implementation of BayesianRidge Nuisance Filtering.
    Notes:
        The processing order is as below:
        1. Nuisance signal filtering with polynomial and given noise source(ort).
        2. Bandpass or Highpass filter if bandcut argument got value.
        3. Image smoothing with Gaussian Kernel with given FWHM if fwhm argument got value.

    Args:
        input: file path of input data (.nii or .nii.gz)
        output: file path for output destination (.nii or .nii.gz)
        mask: file path of mask image (.nii or .nii.gz)
        bandcut: frequency range for bandpass filter, if it only got one float value, then performing highpass filter.
        fwhm: Full-Width at Half-Maximum for spatial smoothing
        dt: sampling time
        bp_order: order for butterfly filter
        ort: optional regressor if you have any
        pn_order: order for polynomial regressor
        stdout: IO stream for message
        stderr: IO stream for error message
    Returns:
        0 if success else 1
    """
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    stdout.write('[UNCCH_CAMRI] Nuisance Filtering:\n')
    stdout.write('')
    try:
        img = nib.load(input)
        funcobjs = []
        if dt is None:
            dt = img.header['pixdim'][4]
        stdout.write(f'  Temporal resolution: {dt} sec\n')

        if pn_order is not None:
            stdout.write('  GLM regression scheduled.]\n')
            stdout.write(f'  - order of polynomial filter: {pn_order}\n')
            stdout.write('  - selected estimator: BayesianRidge\n')
            if ort is not None:
                stdout.write('  - Adding nuisance regressor to design matrix.\n')
                stdout.write(f'  - Regressor path: {ort}\n')
                ort = load(ort)
            else:
                stdout.write('  - No additional regressor.\n')
            nr_obj = get_funcobj(nuisance_regression,
                                 estimator=BayesianRidge,
                                 ort=ort,
                                 order=pn_order)
            funcobjs.append(nr_obj)
        else:
            stdout.write('  Skipping GLM regression.\n')
        if bandcut is not None:
            if isinstance(bandcut, list):
                stdout.write('  Bandpass filter scheduled.\n')
                stdout.write(f'  - Band Frequencies: {bandcut}Hz\n')
            else:
                stdout.write('  Highpass filter scheduled.\n')
                stdout.write(f'  - Cut Frequency: {bandcut}Hz\n')
            if bp_order is None:
                raise InvalidApproach('The order for butterfly filter must be provided.')
            bp_obj = get_funcobj(bandpass,
                                 bandcut=bandcut,
                                 dt=dt,
                                 order=bp_order)
            funcobjs.append(bp_obj)
        else:
            stdout.write('  Skipping bandpass filter.\n')

        func_img = np.asarray(img.dataobj)
        if mask is not None:
            mask_img = np.asarray(nib.load(mask).dataobj)
        else:
            mask_img = None
        stdout.write('  Processing...\n')
        filtered_img = apply_funcobj(funcobjs, func_img, mask_img, io_handler=stdout)
        filtered_nii = nib.Nifti1Image(filtered_img, img.affine)
        filtered_nii._header = img.header.copy()

        if fwhm is not None:
            stdout.write('  Performing spatial smoothing.\n')
            stdout.write(f'  - FWHM: {fwhm} mm\n')
            sitk_img, header = nib2sitk(filtered_nii)
            filtered_sitk_img = gaussian_smoothing(sitk_img, fwhm, io_handler=stdout)
            filtered_nii = sitk2nib(filtered_sitk_img, header)
    except:
        stderr.write('[ERROR] Failed.\n')
        import traceback
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    filtered_nii.to_filename(output)
    stdout.write('Done...\n')
    return 0


def signal_cleaning_func(input_path, output_path, mask_path,
                         confound_param=None,
                         mparam_path=None,
                         low_pass=None, high_pass=None, tr=None,
                         standardize=True,
                         stdout=None, stderr=None):
    """
    Documentation

    wrapper code for Nilearn signal.clean
    """
    # --- import module here
    from nilearn import signal, masking
    import numpy as np
    import nibabel as nib
    import slfmri.lib.io as slio

    # --- io handler
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    try:
        # --- put your main code here

        # load data
        img_obj = nib.load(input_path)
        mask_obj = nib.load(mask_path)
        mask_indice = np.nonzero(np.asarray(mask_obj.dataobj))

        stdout.write(f'Input: {input_path}\n')
        stdout.write(f'Mask: {mask_path}\n')
        # we encourage to print out output every step for debugging

        masked_data = masking.apply_mask(img_obj, mask_obj)

        # confounds estimation
        if confound_param is None:
            confound_param = dict(n_confounds=5, percentile=2.0, detrend=True)
        confounds_obj = signal.high_variance_confounds(masked_data, **confound_param)
        stdout.write(f'Confound estimation processed:\n')
        for k, v in confound_param.items():
            stdout.write(f'\t{k}: {v}\n')

        # concat motion parameters to confounds
        if mparam_path is not None:
            mparam_obj = slio.load(mparam_path)
            confounds_obj = np.concatenate([confounds_obj, mparam_obj.to_numpy()], axis=-1)
            stdout.write(f'Motion parameter loaded: {mparam_path}\n')

        # parse tr from header
        if tr is None:
            tr = img_obj.header['pixdim'][4]
        stdout.write(f'Temporal resolution: {tr} sec\n')

        if high_pass is not None:
            stdout.write(f'Highpass filter: {high_pass} Hz\n')
        if low_pass is not None:
            stdout.write(f'Lowpass filter : {low_pass} Hz\n')
        stdout.write(f'standardize: {standardize}\n\n')

        # confound cleaning
        stdout.write(f'Data cleaning....\n\n')
        cleaned_signals = signal.clean(masked_data, confounds=confounds_obj,
                                       high_pass=high_pass, low_pass=low_pass, t_r=tr,
                                       standardize=standardize)
        # resamble the Niilike obj
        output_data = np.zeros(img_obj.shape)
        output_data[mask_indice] = cleaned_signals.T

        output_nii = nib.Nifti1Image(output_data, header=img_obj._header, affine=img_obj.affine)

        stdout.write(f'Saving data to: {output_path}\n')
        output_nii.to_filename(output_path)
        stdout.write(f'Done!')

        # -- until here
    except:
        # Error handler
        stderr.write('[ERROR] Failed.\n')
        import traceback
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    return 0

if __name__ == '__main__':
    file_path = '../../../slfmri/examples/camri_isotropic_epi.nii.gz'
    nf_output = '../../../slfmri/examples/nuisance_filtered.nii.gz'
    nuisance_filtering_func(file_path, nf_output, fwhm=0.5, bandcut=0.01)

