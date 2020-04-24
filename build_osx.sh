cmake --build . --config Release
mv *.so build/lib.macosx-10.14-x86_64-3.7/
pip3 install -e . --user
