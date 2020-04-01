#Telex-Python 

##Build

Clone Telex-framework (https://github.com/mmertama/Telex-framework.git)
build using cmake in OSX or Linux, for Windows run associated msvc_build.bat in MSVC x64 terminal)
Clone Telex-Python (https://github.com/mmertama/Telex-Python.git)
In Linux
cmake --build . --config Release
mv *.so build/lib.linux-x86_64-3.6/
pip3 install -e . --user
(or run .build.sh) 
Other platforms TBD

