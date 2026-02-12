import os
import subprocess
from setuptools import setup, find_packages
import torch
from torch.utils.cpp_extension import BuildExtension, CUDAExtension, CUDA_HOME

def get_compiler_type():
    cxx = os.environ.get('CXX', 'g++')
    try:
        out = subprocess.check_output([cxx, '--version'], stderr=subprocess.STDOUT).decode()
        if 'icpx' in out or 'oneAPI' in out or 'Intel' in out:
            return 'intel'
        if 'clang' in out:
            return 'clang'
    except Exception:
        pass
    return 'gcc'

compiler_type = get_compiler_type()

cxx_flags = ['-std=c++17', '-O3']
nvcc_flags = ['-std=c++17']

if compiler_type == 'intel':
    nvcc_flags += ['--allow-unsupported-compiler']
    cxx_flags += ['-fp-model=precise']
elif compiler_type == 'gcc':
    cxx_flags += ['-Wno-deprecated-declarations']

if not torch.cuda.is_available():
    ext_modules = None
elif torch.cuda.is_available() and CUDA_HOME is not None:
    ext_modules = [
        CUDAExtension(
            name='se3cnn.real_spherical_harmonics',
            sources=[
                'src/real_spherical_harmonics/rsh_bind.cpp',
                'src/real_spherical_harmonics/rsh_cuda.cu'
            ],
            extra_compile_args={
                'cxx': cxx_flags,
                'nvcc': nvcc_flags
            }
        )
    ]
else:
    ext_modules = None

setup(
    name='se3cnn',
    url='https://github.com/mariogeiger/se3cnn',
    author='Mario Geiger',
    install_requires=[
        'scipy',
        'appdirs'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExtension},
    packages=find_packages(),
)
