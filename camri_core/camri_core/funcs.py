from slfmri.lib.volume import modenorm
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


def modenorm_func(input: str, output: str, mask: Optional[str] = None,
                  mode: int = 1000,
                  stdout: Optional[IO] = None,
                  stderr: Optional[IO] = None):
    """ FSL's Mode normalization python implementation.
    Args:
        input:
        output:
        mask:
        mode:
        stdout:
        stderr:

    Returns:

    """
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    stdout.write('[UNCCH_CAMRI] Mode Normalization:\n')
    stdout.write(f'  Input path  : {input}\n')
    stdout.write(f'  Output path : {output}\n')

    try:
        img = nib.load(input)
        func_img = np.asarray(img.dataobj)

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
    except:
        import traceback
        stderr.write('[ERROR] Failed.\n')
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1

    normed_nii = nib.Nifti1Image(normed_img, img.affine)
    normed_nii._header = img.header.copy()
    normed_nii.to_filename(output)
    stdout.write('Done...\n'.format(output))
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
                stdout.write(f'  - Band Frequencies: {bandcut[0]}-{bandcut[1]}Hz\n')
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


if __name__ == '__main__':
    file_path = '../../../slfmri/examples/camri_isotropic_epi.nii.gz'
    nf_output = '../../../slfmri/examples/nuisance_filtered.nii.gz'
    nuisance_filtering_func(file_path, nf_output, fwhm=0.5, bandcut=0.01)

