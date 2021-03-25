cmake CMakeLists.txt
cmake --build . --config Release
OS_VER_LONG=$(defaults read loginwindow SystemVersionStampAsString)
OS_VER=$(echo "${OS_VER_LONG}" | grep -o '[0-9]\+.[0-9]\+')
PY_VER_LONG=$(python3 --version)
PY_VER=$(echo "${PY_VER_LONG}" | grep -o '[0-9]\+.[0-9]\+')
cp *.so build/lib.macosx-${OS_VER}-x86_64-${PY_VER}
pip3 install -e . --user
