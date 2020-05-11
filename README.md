# Telex-Python 

## Build

Clone Telex-framework (https://github.com/mmertama/Telex-framework.git)
Build using cmake in OSX or Linux, for Windows run associated msvc_build.bat in MSVC x64 terminal)
Clone Telex-Python (https://github.com/mmertama/Telex-Python.git)
Build scripts are for spesific OS/Python versions - but they are only three lines and shall not be a problem. 

For example Linux looks something like this
<pre>
cmake --build . --config Release
mv *.so build/lib.linux-x86_64-3.6/
pip3 install -e . --user
</pre>

Then run some of the python scripts in test folder to if UI opens. 

## API

The programming interface is very same as in Telex-framework (https://github.com/mmertama/Telex-framework.git) - except I changed function and method names from CamelCase to more pythonic snake_case (Im not sure if that was a right choice, but its not a big deal). Please look 
Telex-framework (https://github.com/mmertama/Telex-framework.git) for documentation. Note that Telex-Utils is not implemented in Python, it has C++ utlitieis and thus that applicable for Python programmers. Otherwise Python-Core (https://github.com/mmertama/Telex-framework/blob/master/telex.md) and Python-Graphics (https://github.com/mmertama/Telex-framework/blob/master/telex_graphics.md) are almost entirely available in Python.  


