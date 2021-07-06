PYDEV_INSTALLED=$(dpkg-query -W -f='${Status}' python3-dev 2>/dev/null | grep -c "ok installed")
if [[ "$PYDEV_INSTALLED" -eq "0" ]]; then
  echo "Python3 dev is missing...apt-get install it, please"	
  sudo apt-get install python3-dev  # for python3.x installs
fi	

PIP3_INSTALLED=$(dpkg-query -W -f='${Status}' python3-pip 2>/dev/null | grep -c "ok installed")
if [[ "$PIP3_INSTALLED" -eq "0" ]]; then
   echo "Pip3 is missing...apt-get install it, please"	
   sudo apt-get install python3-pip 
fi	

mkdir -p build
pushd build

if [[ ! $(find /usr -name "gempyreConfig.cmake" 2>/dev/null) ]]; then
  git clone https://github.com/mmertama/Gempyre.git
  pushd Gempyre
  ./linux_install.sh
  popd
fi


PY_VER_LONG=$(python3 --version)
PY_VER=$(echo "${PY_VER_LONG}" | grep -o '[0-9]\+.[0-9]\+')

cmake .. -DCMAKE_BUILD_TYPE=RELEASE
cmake --build . --config Release

mkdir -p lib.linux-x86_64-${PY_VER}
cp ./Gempyre.cpython-*.so lib.linux-x86_64-${PY_VER}/

pip3 install -e .. --user

popd
