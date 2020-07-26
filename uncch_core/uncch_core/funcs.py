from slfmri.lib.utils import get_funcobj, apply_funcobj
from slfmri.lib.io import load
from shleeh.utils import user_warning
from shleeh.errors import *
import nibabel as nib
import numpy as np
import sys
from typing import Optional, Union, IO


def periodogram_func(input, output, mask=None,
                     dt=2, nfft=100,
                     stdout=None, stderr=None):
    """ Calculate tSNR
        Args:
            input: file path of input data (.nii or .nii.gz)
            output: file path for output destination (.nii or .nii.gz)
            mask: file path of mask image (.nii or .nii.gz)
            stdout: IO stream for message
            stderr: IO stream for error message
        Returns:
            0 if success else 1
    """
    from scipy.signal import periodogram

    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    stdout.write('[UNCCH_CAMRI] Voxel-wise Periodogram:\n')
    try:
        fs = 1 / dt
        input_nii = nib.load(input)
        if mask is None:
            mask_data = (np.asarray(input_nii.dataobj).mean(-1) != 0).astype(int)
        else:
            mask_nii = nib.load(mask)
            mask_data = np.asarray(mask_nii.dataobj)

        input_data = np.asarray(input_nii.dataobj)
        output_data = np.zeros(mask_data.shape)
        indices = np.transpose(np.nonzero(mask_data))
        hz_dim = False

        for x, y, z in indices:
            f, pxx = periodogram(input_data[x, y, z, :], fs=fs, nfft=nfft)
            if not hz_dim:
                hz_dim = np.diff(f).mean()
            if len(output_data.shape) == 3:
                output_data = np.concatenate([output_data[:, :, :, np.newaxis]] * f.shape[0], axis=-1)
            output_data[x, y, z, :] = pxx

        output_nii = nib.Nifti1Image(output_data, affine=input_nii.affine, header=input_nii.header)
        output_nii.header.set_xyzt(t=32)  # Hz
        output_nii.header['pixdim'][4] = hz_dim
        output_nii.to_filename(output)
        stdout.write('Done...\n'.format(output))

    except:
        import traceback
        stderr.write('[ERROR] Failed.\n')
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    return 0


def tsnr_func(input: str, output: str, mask: Optional[str] = None,
              stdout: Optional[IO] = None, stderr: Optional[IO] = None):
    """ Calculate tSNR
    Args:
        input: file path of input data (.nii or .nii.gz)
        output: file path for output destination (.nii or .nii.gz)
        mask: file path of mask image (.nii or .nii.gz)
        stdout: IO stream for message
        stderr: IO stream for error message
    Returns:
        0 if success else 1
    """
    from slfmri.lib.volume import vol_tsnr

    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    stdout.write('[UNCCH_CAMRI] tSNR calculation:\n')
    try:
        img = nib.load(input)
        func_img = np.asarray(img.dataobj)
        stdout.write(f'  Input path  : {input}\n')
        if mask is not None:
            stdout.write(f'  Mask_path   : {mask}\n')
            mask_img = np.asarray(nib.load(mask).dataobj)
        else:
            stdout.write('  No Mask file was provided.\n')
            mask_img = None
        tsnr_img = vol_tsnr(func_img, mask_img, io_handler=stdout)
        stdout.write(f'  Output path : {output}\n')
        tsnr_nii = nib.Nifti1Image(tsnr_img, img.affine)
        tsnr_nii._header = img.header.copy()
        tsnr_nii.to_filename(output)
        stdout.write('Done...\n'.format(output))
    except:
        import traceback
        stderr.write('[ERROR] Failed.\n')
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    return 0


def standardize_func(input: str, output: str, mask: Optional[str] = None,
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
    from slfmri.lib.volume import vol_standardize

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
        normed_img = vol_standardize(func_img, mask_img, io_handler=stdout)
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
                  stdout: Optional[IO] = None, stderr: Optional[IO] = None):
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
    from slfmri.lib.volume import vol_modenorm

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
        normed_img = vol_modenorm(func_img, mask_img, mode, io_handler=stdout)
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


def nuisance_regression_func(input: str, output: str, mask: Optional[str] = None,
                             highpass: Optional[float] = None, lowpass: Optional[float] = None,
                             bp_order: Optional[int] = 5, dt: Optional[Union[int, float]] = None,
                             ort: Optional[str] = None, pn_order: Optional[int] = 3,
                             fwhm: Optional[float] = None,
                             stdout: Optional[IO] = None, stderr: Optional[IO] = None):
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
        highpass: high-pass cutoff frequency
        lowpass: low-pass cutoff frequency
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
    from sklearn.linear_model import BayesianRidge
    from slfmri.lib.signal import bandpass, nuisance_regression
    from slfmri.lib.volume.man import nib2sitk, sitk2nib, gaussian_smoothing

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
        if highpass and lowpass:
            stdout.write('  Bandpass filter scheduled.\n')
            stdout.write(f'  - Band Frequencies: {highpass} - {lowpass}Hz\n')
        else:
            if highpass:
                stdout.write('  High-pass filter scheduled.\n')
                stdout.write(f'  - Cut Frequency: {highpass}Hz\n')
            if lowpass:
                stdout.write('  Low-pass filter scheduled.\n')
                stdout.write(f'  - Cut Frequency: {lowpass}Hz\n')

        if highpass or lowpass:
            if not bp_order:
                raise InvalidApproach('The order for butterfly filter must be provided.')
            bp_obj = get_funcobj(bandpass,
                                 highpass=highpass,
                                 lowpass=lowpass,
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

        stdout.write(f'  Output path : {output}\n')
        filtered_nii.to_filename(output)
        stdout.write('Done...\n')
    except:
        stderr.write('[ERROR] Failed.\n')
        import traceback
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    return 0


def reho_func(input: str, output: str, mask: Optional[str] = None, nn_level: int = 3,
              stdout: Optional[IO] = None, stderr: Optional[IO] = None):
    # --- import module here
    from slfmri.lib.volume import reho
    stdout.write('[UNCCH_CAMRI] ReHo calculation:\n')
    # --- io handler
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    try:
        # --- put your main code here
        img = nib.load(input)
        func_img = np.asarray(img.dataobj)
        stdout.write(f'  Input path  : {input}\n')
        if mask is not None:
            stdout.write(f'  Mask_path   : {mask}\n')
            mask_img = np.asarray(nib.load(mask).dataobj)
        else:
            stdout.write('  No Mask file was provided.\n')
            mask_img = None
        reho_img = reho(func_img, mask_img, nn=nn_level)
        stdout.write(f'  Output path : {output}\n')
        reho_nii = nib.Nifti1Image(reho_img, img.affine)
        reho_nii._header = img.header.copy()
        reho_nii.to_filename(output)
        stdout.write('Done...\n'.format(output))
        # -- until here
    except:
        # Error handler
        stderr.write('[ERROR] Failed.\n')
        import traceback
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    return 0


def alff_func(input: str, output:str, mask: Optional[str] = None,
              highpass: float = 0.01, lowpass: float = 0.1,
              dt: Optional[Union[int, float]] = None,
              stdout=None, stderr=None):
    """ ALFF is defined as the sum of amplitudes of each voxel's signal frequency spectrum
    within the low-frequency range (Zang et al., 2007) and reflects
    the amplitude of spontaneous low-frequency fluctuations in the BOLD signal.

    Args:
        input: file path of input data (.nii or .nii.gz)
        output: file path for output destination (.nii or .nii.gz)
        mask: file path of mask image (.nii or .nii.gz)
        highpass: high-pass cutoff frequency
        lowpass: low-pass cutoff frequency
        dt: sampling time
        stdout: IO stream for message
        stderr: IO stream for error message
    Returns:
        0 if success else 1
    """
    from slfmri.lib.signal import alff

    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    stdout.write('[UNCCH_CAMRI] ALFF:\n')
    try:
        stdout.write(f'  Input path  : {input}\n')
        input_nii = nib.load(input)

        if mask is None:
            mask_data = (np.asarray(input_nii.dataobj).mean(-1) != 0).astype(int)
        else:
            stdout.write(f'  Mask_path   : {mask}\n')
            mask_data = np.asarray(nib.load(mask).dataobj)

        if dt is None:  # if no dt, parse from header
            dt = input_nii.header['pixdim'][4]

        input_data = np.asarray(input_nii.dataobj)
        output_data = np.zeros(mask_data.shape)
        indices = np.transpose(np.nonzero(mask_data))

        for x, y, z in indices:
            alff_ = alff(input_data[x, y, z], dt=dt, band=[highpass, lowpass])
            output_data[x, y, z] = alff_

        # Standardize
        all_data = output_data[np.nonzero(mask_data)]

        avr = all_data.mean()
        std = all_data.std()

        output_data[np.nonzero(mask_data)] = (all_data - avr) / std
        output_nii = nib.Nifti1Image(output_data, affine=input_nii.affine, header=input_nii.header)
        stdout.write(f'  Output path  : {output}\n')
        output_nii.to_filename(output)
        stdout.write('Done...\n')
    except:
        import traceback
        stderr.write('[ERROR] Failed.\n')
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    return 0


def dvars_func(input: str, output: str, mask: Optional[str] = None,
               stdout: Optional[IO] = None, stderr: Optional[IO] = None):
    # --- import module here
    from slfmri.lib.volume import dvars, bold_mean_std
    import pandas as pd

    # --- io handler
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    stdout.write('[UNCCH_CAMRI] DVARS:\n')
    try:
        # --- put your main code here
        stdout.write(f'  Input path  : {input}\n')
        input_nii = nib.load(input)
        input_data = np.asarray(input_nii.dataobj)

        if mask is None:
            mask_data = None
        else:
            stdout.write(f'  Mask_path   : {mask}\n')
            mask_data = nib.load(mask).dataobj

        df = pd.DataFrame()
        stdout.write('')
        df['DVARs'] = dvars(input_data, mask_data)
        mean, std = bold_mean_std(input_data, mask_data)
        df['BOLD_Mean'] = mean
        df['BOLD_STD'] = std
        stdout.write(f'  Output path  : {output}\n')
        df.to_csv(output, sep='\t', index=False)
        stdout.write('Done...\n')
        # -- until here
    except:
        # Error handler
        stderr.write('[ERROR] Failed.\n')
        import traceback
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    return 0


def fd_func(input: str, output: str, mean_radius=None,
            stdout: Optional[IO] = None, stderr: Optional[IO] = None):
    # --- import module here
    from slfmri.lib.signal.qc import framewise_displacements, convert_radian2distance
    import pandas as pd

    stdout.write('[UNCCH_CAMRI] Framewise Displacement:\n')
    # --- io handler
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    try:
        # --- put your main code here
        stdout.write(f'  Input path  : {input}\n')
        volreg = pd.read_csv(input, header=None, sep=r'\s+')
        volreg.columns = ['Roll', 'Pitch', 'Yaw', 'dI-S', 'dR-L', 'dA-P']
        if mean_radius is None:
            # default for rat
            mean_radius = np.round(np.sqrt(2) * 9)
            stdout.write('  No input provided on mean_radius, using default value for Rats\n')
            stdout.write('  For the other cases, input the appropriate value.\n')
        stdout.write(f'  MeanRadius   : {mean_radius}\n')

        volreg = convert_radian2distance(volreg, mean_radius)
        fd_metrics = framewise_displacements(volreg)
        stdout.write(f'  Output path  : {output}\n')
        fd_metrics.to_csv(output, sep='\t', index=False)
        stdout.write('Done...\n')
        # -- until here
    except:
        # Error handler
        stderr.write('[ERROR] Failed.\n')
        import traceback
        traceback.print_exception(*sys.exc_info(), file=stderr)
        return 1
    return 0


if __name__ == '__main__':
    pass

