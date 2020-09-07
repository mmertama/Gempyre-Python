# Gempyre-Python 

## Build

Clone Gempyre-Python (https://github.com/mmertama/Gempyre-Python.git)

Build scripts are for spesific OS/Python versions - but they are only three lines and shall not be a problem.

For example Linux script looks something like this
<pre>
cmake --build . --config Release
mv *.so build/lib.linux-x86_64-3.6/
pip3 install -e . --user
</pre>

### For Linux
* $ git clone https://github.com/mmertama/Gempyre-Python.git
* $ ./build_linux.sh

### For MacOS
* $ git clone https://github.com/mmertama/Gempyre-Python.git
* $ ./build_osx.sh

### For Windows:
* install git bash https://gitforwindows.org/
* $ git clone https://github.com/mmertama/Gempyre-Python.git
* install cmake https://cmake.org/download/ (let it to be added in path)
* install Visual Studio https://docs.microsoft.com/en-us/cpp/build/vscpp-step-0-installation?view=vs-2019
		* pick Desktop development with C++
* install Python 3.8 (3.6 >= shall be ok) https://www.python.org/downloads/windows/
* Open x64 Native Tools Command Prompt for VS 2019
* run msvc_build at Gempyre-Python folder

### Run

After install, you just run the script!

<pre>
$ python3 test/python_test_1.html
</pre>

## API

The programming interface is very same as in [Gempyre](https://github.com/mmertama/Gempyre.git)
- except I changed function and method name naming from CamelCase to more pythonic snake_case (Im not sure if that was a right choice).

Please look  [Gempyre](https://github.com/mmertama/Gempyre.git) for documentation.

Please note that Gempyre Core and Gempyre Graphics are part of Python API, but not Gempyre-Utils, it has C++ utilites and thus not applicable for Python programmers as everything and more is already there!
  


