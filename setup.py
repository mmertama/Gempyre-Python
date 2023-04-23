
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import os
import sys
import platform
import subprocess


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir = ''):
        Extension.__init__(self, name, sources = [])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)
        super().run()

    def finalize_options(self):
        super().finalize_options()
        self.build_lib = os.path.dirname(os.path.abspath(__file__)) + '/build'

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']      
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        print("Using temp:", self.build_temp)


setup (name='Gempyre',
       version='1.2.0',
       license='MIT',
       description='Gempyre Framework',
       author='Markus Mertama',
       author_email='foobar@foobar',
       url='https://github.com/mmertama',
       long_description='''
Gempyre is C++ Framework for quick and simple UI development and Gempyre-Python apply that breeze to Python development.
''',
       packages=find_packages(),
       ext_modules=[CMakeExtension('Gempyre')],
       cmdclass={'build_ext': CMakeBuild},
       setup_requires=['wheel'],
       install_requires=['pywebview', 'websockets'],
       entry_points={
           'console_scripts': ['pyclient=client.pyclient:main']}
      )
       
