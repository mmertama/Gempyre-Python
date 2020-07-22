cmake CMakeLists.txt
cmake --build . --config Release
OS_VER_LONG=$(defaults read loginwindow SystemVersionStampAsString)
OS_VER=$(echo "${OS_VER_LONG}" | grep -o '[0-9]\+.[0-9]\+')
PY_VER_LONG=$(python3 --version)
PY_VER=$(echo "${PY_VER_LONG}" | grep -o '[0-9]\+.[0-9]\+')
#mv Telex.so  build/lib.macosx-10.15-x86_64-3.8/Telex.cpython-38-darwin.so
mv *.so build/lib.macosx-${OS_VER}-x86_64-${PY_VER}/
pip3 install -e . --user
