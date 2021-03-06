import brian2
import os
import shutil
import sys
from brian2.tests.features import (Configuration, DefaultConfiguration,
                                   run_feature_tests, run_single_feature_test)

__all__ = ['CUDAStandaloneConfiguration']

class CUDAStandaloneConfiguration(Configuration):
    name = 'CUDA standalone'
    def before_run(self):
        brian2.set_device('cuda_standalone', build_on_run=False)
        
    def after_run(self):
        if os.path.exists('cuda_standalone'):
            shutil.rmtree('cuda_standalone')
        brian2.device.build(directory='cuda_standalone', compile=True, run=True)

