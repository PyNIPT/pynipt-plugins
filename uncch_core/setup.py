#!/usr/scripts/env python
"""
PyNIPT plugin - UNCCH
"""
# import sys
# if sys.platform == 'win32':
#     raise OSError

from distutils.core import setup
from setuptools import find_packages

__version__ = '0.0.1'
__author__ = 'SungHo Lee'
__email__ = 'shlee@unc.edu'
__url__ = 'https://github.com/dvm-shlee/pynipt-plugin'
__package_name__ = 'uncch_core'

setup(name=f'pynipt-plugin-{__package_name__}',
      version=__version__,
      description='UNCCH fMRI pipeline',
      python_requires='>3.5, <3.8',
      author=__author__,
      author_email=__email__,
      url=__url__,
      license='GNLv3',
      packages=find_packages(),
      install_requires=['pynipt>=0.2.2',
                        'nibabel',
                        'simpleITK',
                        'rbm>=0.0.2a0',
                        'shleeh>=0.0.7',
                        'slfmri>=0.0.5'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows :: Windows 10',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development',
      ],
      keywords='pynipt, plugin, pipeline, uncch_core, windows10, windows'
     )
