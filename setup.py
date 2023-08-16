from setuptools import find_packages
from skbuild import setup  # This line replaces 'from setuptools import setup'
import os

setup (name='Gempyre',
       version='1.2.6',
       #license='MIT',
       description='Gempyre Framework',
       #author='Markus Mertama',
       #author_email='foobar@foobar',
       url='https://github.com/mmertama',
       long_description='''
Gempyre is C++ Framework for quick and simple UI development and Gempyre-Python apply that breeze to Python development.
''',
       packages=find_packages(),
       #package_dir={"": "_skbuild/linux-x86_64-3.8/cmake-install"},
       #cmake_install_dir="Gempyre",
       #python_requires=">=3.8",	
       #packages=find_packages(),
       #ext_modules=[CMakeExtension('Gempyre')],
       #cmdclass={'build_ext': CMakeBuild},
       #setup_requires=['wheel'],
       #install_requires=['pywebview', 'websockets'],
       #entry_points={
       #    'console_scripts': ['pyclient=client.pyclient:main']}
      )
       
