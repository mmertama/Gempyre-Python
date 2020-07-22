cmake --build . --config Release
OS_VER_LONG=$(defaults read loginwindow SystemVersionStampAsString)
PY_VER_LONG=$(python --version) 
OS_VER=10.15
PY_VER=3.8
mv Telex.so  build/lib.macosx-10.15-x86_64-3.8/Telex.cpython-38-darwin.so
#mv *.so build/lib.macosx-${OS_VER}-x86_64-${PY_VER}/
pip3 install -e . --user
