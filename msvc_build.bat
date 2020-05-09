cmake CMakeLists.txt -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
move /Y Release\*.pyd build\lib.win-amd64-3.8
pip3 install -e . --user

