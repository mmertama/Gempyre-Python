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

#        if platform.system() == "Windows":
#            subprocess.check_call(['runas /user:administratorcmake', ext.sourcedir] + cmake_args, cwd = self.build_temp)
 #           subprocess.check_call(['runas /user:administrator cmake', '--build', '.'] + build_args, cwd = self.build_temp)
#        else:
        #subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd = self.build_temp)
        #subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd = self.build_temp)

        
        
setup (name = 'Telex',
       version = '1.0.1',
       description = 'Telex Framework',
       author = 'Markus Mertama',
       author_email = 'foobar@foobar',
       url = 'https://github.com/mmertama',
       long_description = '''
Telex is C++ Framework for quick and simple UI development and Telex-Python apply that breeze to Python development.
''',
      packages = find_packages(),
      ext_modules = [CMakeExtension('Telex')],
      cmdclass = {'build_ext': CMakeBuild}
  #    setup_requires=['wheel', 'sdist']
      )
       
