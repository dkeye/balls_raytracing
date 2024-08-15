from setuptools import setup
from Cython.Build import cythonize

setup(
    name="ball ray tracing",
    ext_modules=cythonize("cython_components/*.pyx", language_level="3"),
)
