
from skbuild import setup  # This line replaces 'from setuptools import setup'

setup (name='Gempyre',
       version='1.2.6',
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
       
