# Gempyre-Python 

The easy and productive UI library for Python. 

## Build

Install Gempyre (https://github.com/mmertama/Gempyre.git), see Gempyre
installation. 

Clone Gempyre-Python (https://github.com/mmertama/Gempyre-Python.git)

You need python3-dev and python3-pip be installed. This may depend on your evironment, e.g. apt-get install python3-dev.

I mostly assume Python 3.8, but if you have python 3.9 installed, then 
    bash```
    pip install --pre pythonnet
    ```
may be needed.

### For Linux
    ```bash
    mkdir -p build
    pushd build
    cmake ..
    cmake --build . --config Release
    pip3 install -e .. --user
    popd
    ```

### For Raspberry OS
    ```bash
    mkdir -p build
    pushd build
    cmake .. -DCMAKE_BUILD_TYPE=RELEASE -DRASPBERRY=1
    cmake --build . --config Release
    pip3 install -e .. --user
    popd
    ```

### For MacOS
  ```bash
  mkdir -p build
  pushd build
  cmake .. -DCMAKE_BUILD_TYPE=RELEASE
  cmake --build . --config Release
  pip3 install -e .. --user
  popd
  ```
  
### For Windows
* For Windows you use either MSVC (at least Visual Studio 19) toolchain, or
MinGW 64-bit. Please note that in Windows you may have several Pythons's installed. 
There may at least be one Windows provided and one that come along MinGW or MSys.

Use respective pip3 of which Python you want to use. In the examples below the MSVC built
is installed to Windows system Python (as started from Command Prompt), and MinGW version is
is installed to MinGW shell as installed within that environment. 

Use 
  ```bat
  py -0p
  ```
and

  ```bash
  which python3
  ```
  
  ```bash
  where python3 
  ```

To figure out the installed Python path.

#### For Windows MSVC
* From Windows menu, Visual Studio: Open "x64 Native Tools Command Prompt for VS 2019"
    ```bash
    if not exist "msvc_build" mkdir msvc_build
    pushd msvc_build
    cmake .. -DCMAKE_BUILD_TYPE=Release
    cmake --build . --config Release
    pip3 install -e .. --user
    popd
    ```

#### For Windows MinGW
* To install pip:
    ```bash
    pacman -S mingw-w64-x86_64-python-pip
    ```
* To install python:
    ```bash
    pacman -S mingw-w64-i686-python3
    ```
* Make sure you are using the right MinGW shell (Msys minGW 64-bit - one with blue icon (Not brown or cyan :-))
    ```bash
    mkdir -p mingw_build
    pushd mingw_build
    $ cmake .. -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DPYTHON_PATH=C:\\msys64\\mingw64\\bin
    cmake --build . --config Release
    pip3 install -e .. --user
    popd
  ```

### Run

After install, you just run the script!

  ```bash
  $ python3 test/telex_test.py
  ```

## API

See examples how to use e.g. [telex_test](https://github.com/mmertama/Gempyre-Python/blob/master/test/telex_test.py)

The programming interface is very same as in [Gempyre](https://github.com/mmertama/Gempyre.git)
- except I changed function and method name naming from CamelCase to more pythonic snake_case (Im not sure if that was a right choice).

Please look  [Gempyre](https://github.com/mmertama/Gempyre.git) for documentation.

Please note that Gempyre Core and Gempyre Graphics are part of Python API, but not Gempyre-Utils, it has C++ utilites and thus not applicable for Python programmers as everything and more is already there!
  
## Examples

### Minimum application

  ```py
  import Gempyre
  import os
  import sys
  from Gempyre_utils import resource

  name = os.path.join(os.path.dirname(sys.argv[0]), "hello.html")
  map, names = resource.from_file(name)
  ui = Gempyre.Ui(map, names[name])
  ui.run()
  ```

#### HTML

Assumed to be found in the same folder as the script

  ```html
  <!DOCTYPE html>
  <html>
    <head>
      <meta charset="utf-8">
    </head>
    <body>
      <script src="/gempyre.js"></script>
      Hello!
    </body>
  </html>
  ```

### Application with interaction
#### Python
```py

def main():
    name = os.path.join(os.path.dirname(sys.argv[0]), "example2.html")
    map, names = resource.from_file(name)
    ui = Gempyre.Ui(map, names[name])
    output = Gempyre.Element(ui, "output")
    open_button = Gempyre.Element(ui, "open")
    open_button.subscribe("click", lambda _: output.set_html("Hello"))
    ui.run()

if __name__ == "__main__":
    main()
```
#### HTML
  ```html
  <!DOCTYPE html>
  <html>
    <head>
      <meta charset="utf-8">
      <title>test</title>
    </head>
    <body>
      <script src="/gempyre.js"></script>
      <button id="open">Open</button>
      <pre id="output"></pre>
    </body>
  </html>
  ```
