from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

get_peaks = Extension("get_peaks",
                     ["get_peaks.pyx"],
                     extra_compile_args = ["-Ofast"])

multisearch = Extension("multisearch",
                        ["multisearch.pyx", "ahocorasick/ahocorasick.c",
                         "ahocorasick/node.c"],
                        include_dirs=["ahocorasick"])

vector = Extension("vector", ["vector.pyx"])

blaslib = Extension("blaslib", ["blaslib.pyx"],
                    extra_compile_args=["-fopenmp"],
                    extra_link_args=["-fopenmp"])

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [get_peaks, multisearch, vector, blaslib]
)