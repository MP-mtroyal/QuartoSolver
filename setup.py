from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension
import sys
import os

CUDA_HOME = os.environ.get("CUDA_PATH", "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.8")

ext_modules = [
    Pybind11Extension(
        "FastCannon",
        ["FastCannon.cpp"],
        include_dirs=[os.path.join(CUDA_HOME, "include")],
        library_dirs=[os.path.join(CUDA_HOME, "lib", "x64")],
        libraries=["cudart"],
        extra_compile_args=["/std:c++17", "/O2"],
        extra_link_args=["/LIBPATH:" + os.path.join(CUDA_HOME, "lib", "x64")]
    ),
]

setup(
    name="FastCannon",
    ext_modules=ext_modules,
)