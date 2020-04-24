cmake --build . --config Release
mv *.so build/lib.linux-x86_64-3.6/

pip3 install -e . --user
