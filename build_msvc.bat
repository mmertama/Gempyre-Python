rem @echo off
if "%VSCMD_ARG_HOST_ARCH%"=="x64" goto pass_ver

echo Execute in the x64 Native tools command prompt.
goto exit
:pass_ver

if not exist "msvc_build" mkdir msvc_build

pushd msvc_build

if exist "C:\Program Files (x86)\gempyre" goto found
if exist "C:\Program Files\gempyre" goto found

git clone https://github.com/mmertama/Gempyre.git
pushd Gempyre
call msvc_install.bat
popd

:found

cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release

if not exist "..\build\lib.win-amd64-3.8" mkdir ..\build\lib.win-amd64-3.8
move /Y Release\*.pyd ..\build\lib.win-amd64-3.8\ 
pip3 install -e .. --user

popd

:exit
