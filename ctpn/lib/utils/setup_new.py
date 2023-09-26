import numpy as np
from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

try:
    numpy_include = np.get_include()
except AttributeError:
    numpy_include = np.get_numpy_include()

setup(ext_modules=cythonize("bbox.pyx"),include_dirs=[numpy_include])
setup(ext_modules=cythonize("cython_nms.pyx"),include_dirs=[numpy_include])

