from slfmri.lib.io import load
from shleeh.utils import user_warning
from shleeh.errors import *
import nibabel as nib
import numpy as np
import sys
from typing import Optional, Union, IO

# Example
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


if __name__ == '__main__':
    pass

