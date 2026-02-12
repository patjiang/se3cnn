import os
import subprocess
from setuptools import setup, find_packages

def get_compiler_type():
    cxx = os.environ.get('CXX', 'g++')
    try:
        out = subprocess.check_output([cxx, '--version'], stderr=subprocess.STDOUT).decode()
        if any(x in out for x in ['icpx', 'oneAPI', 'Intel']):
            return 'intel'
    except Exception:
        pass
    return 'gcc'

def get_ext_modules():
    try:
        import torch
        from torch.utils.cpp_extension import BuildExtension, CUDAExtension, CUDA_HOME
    except Exception:
        return None, {}

    compiler_type = get_compiler_type()
    cxx_flags = ['-std=c++17', '-O3']
    nvcc_flags = ['-std=c++17']

    if compiler_type == 'intel':
        nvcc_flags += ['--allow-unsupported-compiler']
        cxx_flags += ['-fp-model=precise']
    
    force_build = os.environ.get('FORCE_CUDA_BUILD', '0') == '1'

    if (torch.cuda.is_available() and CUDA_HOME is not None) or force_build:
        ext_modules = [
            CUDAExtension(
                name='se3cnn.real_spherical_harmonics',
                sources=[
                    'src/real_spherical_harmonics/rsh_bind.cpp',
                    'src/real_spherical_harmonics/rsh_cuda.cu'
                ],
                extra_compile_args={'cxx': cxx_flags, 'nvcc': nvcc_flags}
            )
        ]
        return ext_modules, {'build_ext': BuildExtension}
    return None, {}

ext_modules, cmdclass = get_ext_modules()

setup(
    ext_modules=ext_modules,
    cmdclass=cmdclass,
)
