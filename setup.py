from setuptools import find_packages
from skbuild import setup  # This line replaces 'from setuptools import setup'
import os

setup (name='Gempyre',
       version='1.2.6',
       description='Gempyre Framework',
       author='Markus Mertama',
       author_email='current.address@unknown.invalid',
       url='https://github.com/mmertama',
       long_description='''
Gempyre is C++ Framework for quick and simple UI development and Gempyre-Python apply that breeze to Python development.
''',
       packages=["Gempyre", "Gempyre_utils"],
       package_dir={"": "src"},
       cmake_install_dir="src/Gempyre",
      )
