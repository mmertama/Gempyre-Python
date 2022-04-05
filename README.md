# Gempyre-Python 

The easy and productive UI library for Python. 

## Build

Install Gempyre (https://github.com/mmertama/Gempyre.git), see Gempyre
installation. 

Clone Gempyre-Python (https://github.com/mmertama/Gempyre-Python.git)

Build scripts are for spesific OS/Python versions - but they are only three lines and shall not be a problem.

For example Linux script looks something like this
<pre>
cmake --build . --config Release
mv *.so build/lib.linux-x86_64-3.6/
pip3 install -e . --user
</pre>

### For Linux (including Raspberry OS)
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
* install Python 3.7 (3.6 >= shall be ok) https://www.python.org/downloads/windows/
* Open x64 Native Tools Command Prompt for VS 2019
* run msvc_build at Gempyre-Python folder

If you have Python 3.8, the internally used [cefpython3](https://pypi.org/project/cefpython3/) does not support Python 3.8 (other OS alternatives can be used and thus this apply only on Windows). Hopefully the support will be soon available. But meanwhile:
	<code>ui = Gempyre.Ui(map, names[name]) if sys.platform != 'win32' or sys.version_info < (3,8) else Gempyre.Ui(map, names[name], "")
</code>
	when creating a Gempyre, should be a quick workaround. That is use the system browser instead (if nothing else works, Chrome should). The "" parameter set system default, but you can set there any browser call, see [Gempyre Documentation](https://github.com/mmertama/Gempyre/blob/master/gempyre.md#explicit-uiconst-stdstring-indexhtml-const-stdstring-browser-const-stdstring-extraparams---unsigned-short-port--usedefaultport-const-stdstring-root--usedefaultroot).

### Run

After install, you just run the script!

<pre>
$ python3 test/python_test_1.py
</pre>

## API

See examples how to use: [telex_test](https://github.com/mmertama/Gempyre-Python/blob/master/test/telex_test.py)

The programming interface is very same as in [Gempyre](https://github.com/mmertama/Gempyre.git)
- except I changed function and method name naming from CamelCase to more pythonic snake_case (Im not sure if that was a right choice).

Please look  [Gempyre](https://github.com/mmertama/Gempyre.git) for documentation.

Please note that Gempyre Core and Gempyre Graphics are part of Python API, but not Gempyre-Utils, it has C++ utilites and thus not applicable for Python programmers as everything and more is already there!
  
## Examples

### Minimum application

```py
import Gempyre

ui = Gempyre.Ui("example.html")
ui.run()
```

### Application with interaction
#### Python
```py
import Gempyre

def main():
    ui = Gempyre.Ui("example2.html")
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

