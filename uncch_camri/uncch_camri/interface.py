from pynipt import Processor, InterfaceBuilder


class Interface(Processor):
    """command line interface example
    """

    def __init__(self, *args, **kwargs):
        super(Interface, self).__init__(*args, **kwargs)

    def afni_MeanImageCalc(self, input_path, regex=None,
                           range=None, file_idx=0, img_ext='nii.gz',
                           step_idx=None, sub_code=None, suffix=None):
        """Calculate mean intensity image using 3dTstat
        Args:
            input_path(str):    datatype or stepcode of input data
            range(list):        range for averaging (default=None)
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='MeanImageCalculation',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex, ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, group_input=False,
                      idx=file_idx,
                      filter_dict=filter_dict)
        itf.set_output(label='output')
        cmd = ["3dTstat -prefix *[output] -mean"]
        if range is not None:
            if isinstance(range, list) and len(range) is 2:
                start, end = range
                if isinstance(start, int) and isinstance(end, int):
                    itf.set_var(label='start', value=start)
                    itf.set_var(label='end', value=end)
                else:
                    self.logging('warn', 'incorrect range values.')
            else:
                self.logging('warn', 'incorrect range values.')
            cmd.append("*[input]'[*[start]..*[end]]'")
        else:
            cmd.append("*[input]")
        itf.set_cmd(' '.join(cmd))
        itf.set_errterm(['ERROR'])
        itf.set_output_checker()
        itf.run()

    def afni_SliceTimingCorrection(self, input_path,
                                   tr=None, tpattern=None, img_ext='nii.gz',
                                   step_idx=None, sub_code=None, suffix=None):
        """Correct slice timing using afni's 3dTshift command
        Args:
            input_path(str):    datatype or stepcode of input data
            tr(int or float):   sampling rate
            tpattern(str):      slice timing pattern available in 3dTshift
                                (e.g. altplus, altminus, seqplut, seqminus)
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='SliceTimingCorrection',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, group_input=False,
                      filter_dict=dict(ext=img_ext))
        itf.set_output(label='output')
        cmd = ['3dTshift -prefix *[output]']
        if tr is not None:
            itf.set_var(label='tr', value=tr)
            cmd.append('-TR *[tr]')
        if tpattern is not None:
            itf.set_var(label='tpattern', value=tpattern)
            cmd.append('-tpattern *[tpattern]')
        cmd.append('*[input]')
        itf.set_cmd(' '.join(cmd))
        itf.set_errterm(['ERROR'])
        itf.set_output_checker()
        itf.run()

    def afni_MotionCorrection(self, input_path, regex=None,
                              base=0, fourier=True, verbose=True,
                              mparam=True, file_idx=None, img_ext='nii.gz',
                              step_idx=None, sub_code=None, suffix=None):
        """Correct head motion using afni's 3dvolreg command
        Args:
            input_path(str):    datatype or stepcode of input data
            step_idx(int):      stepcode index (positive integer lower than 99)
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            base(int or str):   reference image
            fourier(bool):      Fourior option on for 3dvolreg
            verbose(bool):      if True, print out all processing messages on STERR.log
            mparam(bool):       if True, generate motion parameter file(1D) using same filename
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        if regex is not None:
            filter_dict = dict(ext=img_ext, regex=regex)
        else:
            filter_dict = dict(ext=img_ext)
        itf.init_step(title='MotionCorrection',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, group_input=False, idx=file_idx,
                      filter_dict=filter_dict)
        itf.set_output(label='output')

        cmd = ["3dvolreg -prefix *[output]"]
        if mparam is True:
            itf.set_output(label='mparam', ext='1D')
            cmd.append("-1Dfile *[mparam]")
        if fourier is True:
            cmd.append("-Fourier")
        if verbose is True:
            cmd.append("-verbose")
        if isinstance(base, int):
            # use frame number for the reference
            itf.set_var(label='base', value=base)
        elif isinstance(base, str):
            # use input_path for the reference
            itf.set_static_input(label='base', input_path=base, idx=0,
                                 filter_dict=dict(ext=img_ext))
        cmd.append('-base *[base] *[input]')

        itf.set_cmd(' '.join(cmd))
        itf.set_errterm(['ERROR'])
        itf.set_output_checker()
        itf.run()

    # def camri_BrainMasking(self, input_path, file_idx=None, img_ext='nii.gz',
    #                        step_idx=None, sub_code=None, suffix=None):
    #     """ Estimate brain mask using 2D-UNET,
    #
    #     Args:
    #         input_path(str):    datatype or stepcode of input data
    #         file_idx(int):      index of file if the process need to be executed on a specific file
    #                             in session folder.
    #         img_ext(str):       file extension (default='nii.gz')
    #         step_idx(int):      stepcode index (positive integer lower than 99)
    #         sub_code(str):      sub stepcode, one character, 0 or A-Z
    #         suffix(str):        suffix to identify the current step
    #     """
    #     itf = InterfaceBuilder(self)
    #     itf.init_step(title='BrainMaskEstimate', mode='masking',
    #                   idx=step_idx, subcode=sub_code, suffix=suffix)
    #     itf.set_input(label='input', input_path=input_path, group_input=False, idx=file_idx,
    #                   filter_dict=dict(ext=img_ext))
    #     itf.set_output(label='mask', suffix='_mask')
    #     itf.set_output(label='copy')
    #     itf.set_cmd("rbm *[input] *[mask]")
    #     itf.set_cmd("cp *[input] *[copy]")
    #     itf.set_output_checker(label='mask')
    #     itf.run()

    def afni_SkullStripping(self, input_path, mask_path, regex=None,
                            file_idx=None, img_ext='nii.gz',
                            step_idx=None, sub_code=None, suffix=None):
        """ stripping the skull using brain mask
        Args:
            input_path(str):    datatype or stepcode of input data
            mask_path(str):     stepcode of mask_path
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='SkullStripping', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex,
                               ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        itf.set_input(label='input', input_path=input_path, group_input=False, idx=file_idx,
                      filter_dict=filter_dict)
        itf.set_static_input(label='mask', input_path=mask_path,
                             idx=0, mask=True, filter_dict=dict(regex=r'.*_mask$', ext=img_ext))
        itf.set_output(label='output')
        itf.set_cmd("3dcalc -prefix *[output] -expr 'a*step(b)' -a *[input] -b *[mask]")
        itf.set_errterm(['ERROR'])
        itf.set_output_checker()  # default label='output'
        itf.run()

    def ants_N4BiasFieldCorrection(self, input_path,
                                   file_idx=None, img_ext='nii.gz',
                                   step_idx=None, sub_code=None, suffix=None):
        """ correcting bias field using N4 algorithm of ants package
        Args:
            input_path(str):    datatype or stepcode of input data
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='N4BiasFieldCorrection', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, group_input=False, idx=file_idx,
                      filter_dict=dict(ext=img_ext))
        itf.set_output(label='output')
        itf.set_cmd("N4BiasFieldCorrection -i *[input] -o *[output]")
        itf.set_output_checker()  # default label='output'
        itf.run()

    def afni_Coregistration(self, input_path, ref_path,
                            file_idx=None, img_ext='nii.gz',
                            step_idx=None, sub_code=None, suffix=None):
        """ realign the functional image into anatomical image using 3dAllineate command of
        afni package.
        Args:
            input_path(str):    datatype or stepcode of input data
            ref_path(str):      stepcode of reference data
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='Coregistration', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, group_input=False, idx=file_idx,
                      filter_dict=dict(ext=img_ext))
        itf.set_static_input(label='ref', input_path=ref_path,
                             idx=0, filter_dict=dict(ext=img_ext))
        itf.set_output(label='output')
        itf.set_output(label='tfmat', ext='aff12.1D')
        itf.set_cmd("3dAllineate -prefix *[output] -onepass -EPI -base *[ref] -cmass+xy "
                    "-1Dmatrix_save *[tfmat] *[input]")
        itf.set_errterm(['ERROR'])
        itf.set_output_checker()  # default label='output'
        itf.run()

    def afni_ApplyTransform(self, input_path, ref_path,
                            file_idx=None, img_ext='nii.gz',
                            step_idx=None, sub_code=None, suffix=None):
        """ apply the transform matrix that acquired from 3dAllineate command
        along all input data using 3dAllineate command of afni package.
        Args:
            input_path(str):    datatype or stepcode of input data
            ref_path(str):      stepcode of reference data
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self, n_threads=1)
        itf.init_step(title='ApplyTransform', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, group_input=False, idx=file_idx,
                      filter_dict=dict(ext=img_ext))
        itf.set_static_input(label='ref', input_path=ref_path,
                             idx=0, filter_dict=dict(ext=img_ext))
        itf.set_static_input(label='tfmat', input_path=ref_path,
                             idx=0, filter_dict=dict(ext='aff12.1D'))
        itf.set_output(label='output')
        itf.set_cmd("3dAllineate -prefix *[output] -master *[ref] -1Dmatrix_apply *[tfmat] *[input]")
        itf.set_errterm(['ERROR'])
        itf.set_output_checker()  # default label='output'
        itf.run()

    def afni_SpatialNorm(self, input_path, ref_path,
                         file_idx=None, img_ext='nii.gz',
                         step_idx=None, sub_code=None, suffix=None):
        """ realign subject brain image into standard space using 3dAllineate command
        of afni package
        Args:
            input_path(str):    datatype or stepcode of input data
            ref_path(str):      path for brain template image
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='SpatialNorm', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, group_input=False, idx=file_idx,
                      filter_dict=dict(ext=img_ext))
        itf.set_var(label='ref', value=ref_path)
        itf.set_output(label='output')
        itf.set_output(label='tfmat', ext='aff12.1D')
        cmd = '3dAllineate -prefix *[output] -twopass -cmass+xy -zclip -conv 0.01 -base *[ref] ' \
              '-cost crM -check nmi -warp shr -1Dmatrix_save *[tfmat] *[input]'
        itf.set_cmd(cmd)
        itf.set_errterm(['ERROR'])
        itf.set_output_checker()
        itf.run()

    def afni_ApplySpatialNorm(self, input_path, ref_path,
                              file_idx=None, img_ext='nii.gz',
                              step_idx=None, sub_code=None, suffix=None):
        """ apply transform matrix generated by 3dAllineate along other images
        using same command of afni package
        Args:
            input_path(str):    datatype or stepcode of input data
            ref_path(str):      path for brain template image
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='ApplySpatialNorm', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, group_input=False,
                      idx=file_idx, filter_dict=dict(ext=img_ext))
        itf.set_static_input(label='base', input_path=ref_path,
                             idx=0, filter_dict=dict(ext='nii.gz'))
        itf.set_static_input(label='tfmat', input_path=ref_path,
                             idx=0, filter_dict=dict(ext='aff12.1D'))
        itf.set_output(label='output')
        cmd = '3dAllineate -prefix *[output] -master *[base] -warp shr -1Dmatrix_apply *[tfmat] *[input]'
        itf.set_cmd(cmd)
        itf.set_errterm(['ERROR'])
        itf.set_output_checker()
        itf.run()

    def ants_SpatialNorm(self, input_path, ref_path,
                         file_idx=None, img_ext='nii.gz',
                         step_idx=None, sub_code=None, suffix=None):
        """ realign subject brain image into standard space using antsRegistrationSyN.sh command
        of ants package
        Args:
            input_path(str):    datatype or stepcode of input data
            ref_path(str):      path for brain template image
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self, n_threads=1)
        itf.init_step(title='SpatialNorm', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, group_input=False, idx=file_idx,
                      filter_dict=dict(ext=img_ext))
        itf.set_var(label='ref', value=ref_path)
        itf.set_var(label='thread', value=self._n_threads)
        itf.set_output(label='output', suffix='_', ext=False)
        itf.set_cmd("antsRegistrationSyN.sh -f *[ref] -m *[input] -o *[output] -n *[thread]")
        itf.set_output_checker(suffix='Warped', ext='nii.gz')
        itf.run()

    def ants_ApplySpatialNorm(self, input_path, ref_path,
                              file_idx=None, img_ext='nii.gz',
                              step_idx=None, sub_code=None, suffix=None):
        """ apply transform matrix generated by antsRegistrationSyN.sh along other images
        using WarpTimeSeriesImageMultiTransform command of ants package
        Args:
            input_path(str):    datatype or stepcode of input data
            ref_path(str):      path for brain template image
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='ApplySpatialNorm', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, group_input=False,
                      idx=file_idx, filter_dict=dict(ext=img_ext))
        itf.set_static_input(label='base', input_path=ref_path,
                             idx=0, filter_dict=dict(regex=r'.*_Warped$', ext='nii.gz'))
        itf.set_static_input(label='tfmorph', input_path=ref_path,
                             idx=0, filter_dict=dict(regex=r'.*_1Warp$', ext='nii.gz'))
        itf.set_static_input(label='tfmat', input_path=ref_path,
                             idx=0, filter_dict=dict(ext='mat'))
        itf.set_output(label='output')
        itf.set_cmd("WarpTimeSeriesImageMultiTransform 4 *[input] *[output] -R "
                    "*[base] *[tfmorph] *[tfmat]")
        itf.set_output_checker()
        itf.run()

    def afni_BlurInMask(self, input_path, mask_path, fwhm,
                        file_idx=None, img_ext='nii.gz',
                        step_idx=None, sub_code=None, suffix=None):
        """ FWHM based spatial gaussian smoothing using 3dBlurInMask command of Afni
        Args:
            input_path(str):    datatype or stepcode of input data
            mask_path(str):     path for brain mask image
            fwhm(float):        full width half maximum value
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='BlurInMask', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=dict(ext=img_ext), group_input=False)
        itf.set_var(label='fwhm', value=str(fwhm))
        itf.set_var(label='mask', value=mask_path)
        itf.set_output(label='output')
        itf.set_cmd("3dBlurInMask -prefix *[output] -FWHM *[fwhm] -mask *[mask] *[input]")
        itf.set_errterm(['ERROR'])
        itf.set_output_checker(label='output')
        itf.run()

    def afni_BlurToFWHM(self, input_path, fwhm, file_idx=None, img_ext='nii.gz',
                        step_idx=None, sub_code=None, suffix=None):
        """ FWHM based spatial gaussian smoothing using 3dmerge command of Afni
        Args:
            input_path(str):    datatype or stepcode of input data
            fwhm(float):        full width half maximum value
            file_idx(int):      index of file if the process need to be executed on a specific file
                                in session folder.
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='BlurToFWHM', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path, idx=file_idx,
                      filter_dict=dict(ext=img_ext), group_input=False)
        itf.set_var(label='fwhm', value=str(fwhm))
        itf.set_output(label='output')
        itf.set_cmd("3dmerge -prefix *[output] -doall -1blur_fwhm *[fwhm] *[input]")
        itf.set_output_checker(label='output')
        itf.run()

    def afni_Scailing(self, input_path, mask_path, mean=100, max=200,
                      img_ext='nii.gz',
                      step_idx=None, sub_code=None, suffix=None):
        """ Scaling the time series dataset to have given mean in the mask
        If max value is inputted, the max value will be cut at given value.
        Args:
            input_path(str):    datatype or stepcode of input data
            mask_path(str):     path for brain mask image
            mean(int, float):   desired mean value
            max(int, float):    desired max value
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='Scaling', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        itf.set_input(label='input', input_path=input_path,
                      filter_dict=dict(ext=img_ext), group_input=False)
        itf.set_temporary(label='meanimg')
        itf.set_var(label='mask', value=mask_path)
        itf.set_var(label='mean', value=mean)
        if max is not None:
            itf.set_var(label='max', value=max)
            expr_block = 'c * min(*[max], a/b**[mean])'
        else:
            expr_block = 'c * min(a/b**[mean])'
        itf.set_output(label='output')
        itf.set_cmd("3dTstat -mean -prefix *[meanimg] *[input]")
        itf.set_cmd("3dcalc -a *[input] -b *[meanimg] -c *[mask] -expr '{}' -prefix *[output]".format(expr_block))
        itf.set_errterm(['ERROR'])
        itf.set_output_checker(label='output')
        itf.run()

    def afni_Deconvolution(self, input_path, mask_path,
                           onset_time, model, parameters, polort=2,
                           regex=None, img_ext='nii.gz',
                           step_idx=None, sub_code=None, suffix=None):
        """ General Linear Model analysis using 3dDeconvolve of Afni package
        this interface is for use of single stimulation model only.
        Args:
            input_path(str):    datatype or stepcode of input data
            mask_path(str):     path for brain mask image
            polort(int):        polynomial regressor for detrending
            onset_time(list):   stimulation onset time, list of int (e.g. [10, 50, 90])
            model(str):         response model
            parameters(list):   parameters for response model
            regex(str):         regular express pattern to filter dataset
            img_ext(str):       file extension (default='nii.gz')
            step_idx(int):      stepcode index (positive integer lower than 99)
            sub_code(str):      sub stepcode, one character, 0 or A-Z
            suffix(str):        suffix to identify the current step
        """
        itf = InterfaceBuilder(self)
        itf.init_step(title='Deconvolve', mode='processing',
                      idx=step_idx, subcode=sub_code, suffix=suffix)
        if regex is not None:
            filter_dict = dict(regex=regex,
                               ext=img_ext)
        else:
            filter_dict = dict(ext=img_ext)
        # set input
        itf.set_input(label='input', input_path=input_path,
                      filter_dict=filter_dict, group_input=False)
        # set variables
        itf.set_var(label='mask', value=mask_path)
        itf.set_var(label='polort', value=polort)
        itf.set_var(label='onset_time', value=' '.join(map(str, onset_time)))
        itf.set_var(label='model', value=model)
        itf.set_var(label='parameters', value=','.join(map(str, parameters)))
        # set temporary output
        itf.set_temporary(label='bucket')
        # set main output
        itf.set_output(label='output')
        itf.set_output(label='matrix', ext=False)
        itf.set_cmd("3dDeconvolve -input *[input] -mask *[mask] "
                    "-num_stimts 1 -polort *[polort] -stim_times 1 '1D: *[onset_time]' "
                    "'*[model](*[parameters])' -stim_label 1 STIM -tout -bucket *[bucket] -x1D *[matrix]")
        itf.set_cmd("3dREMLfit -matrix *[matrix].xmat.1D -input *[input] -tout -Rbuck *[output] -verb")
        itf.set_errterm(['ERROR'])
        itf.set_output_checker(label='output')
        itf.run()

    def afni_TTest(self, input_a, regex_a, data_idx_a=1, output_filename=None, mask_path=None,
                   clustsim=True,
                   input_b=None, regex_b=None, data_idx_b=1,
                   img_ext='nii.gz', step_idx=None, sub_code=None, suffix=None):
        """ perform student t-test using 3dttest++ in Afni

        Args:
            input_a(str):           datatype or stepcode of input data of group A
            regex_a(str):           regular express pattern to filter group A
            input_b(str):           datatype or stepcode of input data of group B
            regex_b(str):           regular express pattern to filter group B
            output_filename(str):   output filename
            data_idx_a(int):        index of sub-brick wants to input for group A
            data_idx_b(int):        index of sub-brick wants to input for group B
            step_idx(int):          stepcode index (positive integer lower than 99)
            sub_code(str):          sub stepcode, one character, 0 or A-Z
            suffix(str):            suffix to identify the current step
        """
        itf = InterfaceBuilder(self, relpath=True)
        if input_b is None:
            title = 'OneSampleTTest'
        else:
            title = 'TwoSampleTTest'
        itf.init_step(title=title,
                      idx=step_idx, subcode=sub_code, suffix=suffix,
                      mode='reporting')
        itf.set_input(label='groupA', input_path=input_a, group_input=True,
                      join_modifier=dict(suffix="'[{}]'".format(data_idx_a)),
                      filter_dict=dict(regex=regex_a, ext=img_ext))

        if input_b is not None:
            itf.set_input(label='groupB', input_path=input_b, group_input=True,
                          join_modifier=dict(suffix=f"'[{data_idx_b}]'"),
                          filter_dict=dict(regex=regex_b, ext=img_ext))
            input_sets = '-setA *[groupA] -setB *[groupB]'
        else:
            input_sets = '-setA *[groupA]'
        if clustsim is True:
            option = '-Clustsim'
            # option = '-tempdir *[tempdir] -prefix_clustsim *[temp_prefix] -CLUSTSIM'
            # itf.set_var(label='temp_prefix', value='temporary')
            # itf.set_temporary(label='tempdir', path_only=True)
        else:
            option = ''
        itf.set_output(label='output', modifier=output_filename,
                       ext='nii.gz')
        itf.set_var(label='mask', value=mask_path)
        itf.set_output(label='resid', modifier=output_filename,
                       suffix='_resid', ext='nii.gz')
        itf.set_cmd(f'3dttest++ -mask *[mask] -prefix *[output] {input_sets} '
                    f'-resid *[resid] -ACF {option}')
        itf.set_errterm(['ERROR'])
        itf.set_output_checker()
        itf.run()

    def afni_MultiVarModeling(self, input_path, regex, regex_label, subbrick_idx=1, mask_path=None,
                              output_filename=None, bsVars=None, wsVars=None, glt_codes=None, glf_codes=None,
                              reindex_subj_by=False, n_threads=None,
                              img_ext='nii.gz', step_idx=None, sub_code=None, suffix=None):
        """ perform Group Analysis with Multi-Variable Modeling approach using 3dMVM in Afni
        this interface currently compatible with only within variable and between variable options.
        Args:
            input_path(str):        datatype or stepcode of input data
            regex(raw str):         regular express pattern to filter dataset
                                    (please refer tutorial)
            regex_label(dict):      label and group number to specify columns of data table
                                    (please refer document)
            subbrick_idx(int):      index of sub-brick wants to input
            mask_path(str):         path for brain mask image
            output_filename(str):   output filename
            bsVars(str):            between subject variables
            wsVars(str):            within subject variables
            glt_codes(dict):        glt codes dict(title=code, ...)
            glf_codes(dict):        glf codes dict(title=code, ...)
            reindex_subj_by(str):   one of between subject variable if want to reindex subject id
            n_threads(int):         number of thread for multicore processing
            img_ext(str):           file extension (default='nii.gz')
            step_idx(int):          stepcode index (positive integer lower than 99)
            sub_code(str):          sub stepcode, one character, 0 or A-Z
            suffix(str):            suffix to identify the current step
        """

        import re
        import numpy as np
        import pandas as pd
        from collections import OrderedDict

        itf = InterfaceBuilder(self)
        itf.init_step('MultiVarModeling',
                      idx=step_idx, subcode=sub_code, suffix=suffix, mode='reporting')
        itf.set_input(label='input', input_path=input_path,
                      filter_dict=dict(regex=regex, ext=img_ext),
                      group_input=True)

        # Prepare data table (advanced usage of complex input structure)
        p = re.compile(regex)
        inputs = itf.get_inputs('input')

        df_dict = OrderedDict()
        subj_idx = regex_label.pop('Subj')
        df_dict['Subj'] = [p.search(f).group(subj_idx) for f in inputs]

        for label, idx in regex_label.items():
            df_dict[label] = [p.search(f).group(idx) for f in inputs]

        if reindex_subj_by is not False:
            subjs = np.array(df_dict['Subj'], dtype=object)
            reindex_base = np.array(df_dict[reindex_subj_by])
            reindex_items = list(set(reindex_base))
            offset = 0
            for item in reindex_items:
                sub_set = subjs[reindex_base == item]
                sub_num = sorted(list(set(sub_set)))
                sub_set = ['s{}'.format(i + 1 + offset) for i, n in enumerate(sub_num) for s in sub_set if s == n]
                subjs[reindex_base == item] = sub_set
                offset += len(sub_num)
            df_dict['Subj'] = list(subjs)

        inputs = [f.replace('nii.gz', 'nii.gz[{}]'.format(subbrick_idx)) for f in inputs]
        df_dict['InputFile'] = inputs
        group_df = pd.DataFrame(df_dict)

        datatable_path = 'dataTable_{}.txt'.format(suffix)
        group_df.iloc[0:len(group_df) - 1].to_csv(datatable_path, index=None,
                                                  sep='\t', line_terminator=' \\\n')
        group_df.iloc[[len(group_df) - 1]].to_csv(datatable_path, index=None,
                                                  header=None, sep='\t', mode='a',
                                                  line_terminator='')
        itf.set_var(label='datatable', value=datatable_path)

        cmd = ['3dMVM']
        if n_threads is not None:
            itf.set_var(label='n_thread', value=8)
        cmd.append('-jobs *[n_thread]')
        if mask_path is not None:
            itf.set_var(label='mask', value=mask_path)
            cmd.append('-mask *[mask]')
        itf.set_output(label='output', modifier=output_filename, ext='nii.gz')
        cmd.append('-prefix *[output]')
        if bsVars is not None:
            cmd.append('-bsVars "{}"'.format(bsVars))
        if wsVars is not None:
            cmd.append('-wsVars "{}"'.format(wsVars))
        if glt_codes is not None:
            cmd.append('-num_glt {}'.format(len(glt_codes)))
            for glt_label, (title, code) in enumerate(sorted(glt_codes.items())):
                cmd.append('-gltLabel {0} {1} -gltCode {0} "{2}"'.format(glt_label + 1, title, code))
        if glf_codes is not None:
            cmd.append('-num_glf {}'.format(len(glf_codes)))
            for glf_label, (title, code) in enumerate(sorted(glf_codes.items())):
                cmd.append('-glfLabel {0} {1} -glfCode {0} "{2}"'.format(glf_label + 1, title, code))
        cmd.append('-dataTable @*[datatable]')
        itf.set_cmd(' '.join(cmd))
        itf.set_errterm(['ERROR'])
        itf.set_output_checker(label='output')
        itf.run()
