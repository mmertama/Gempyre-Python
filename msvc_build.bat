@echo off
if "%VSCMD_ARG_HOST_ARCH%"=="x64" goto pass_ver
echo Execute in the x64 Native tools command prompt.
goto exit
:pass_ver

if not exist "msvc_build" mkdir msvc_build

pushd msvc_build

if exists "C:\Program Files(86)\gempyre" goto found
if exists "C:\Program Files\gempyre" goto found

git clone https://github.com/mmertama/Gempyre.git
pushd Gempyre
msvc_install.sh
popd

:found

cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
move /Y Release\*.pyd build\lib.win-amd64-3.8\ TODOOO
pip3 install -e . --user

popd

:exit
