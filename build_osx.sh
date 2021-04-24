# is needed in osx? no? apt-get anyway not working...
#PYDEV=python3-dev
#PYDEV_INSTALLED=$(dpkg-query -W -f='${Status}' $PYDEV 2>/dev/null | grep -c "ok installed")
#if [[ "$PYDEV_INSTALLED" -eq "0" ]]; then
#  echo "Python3 dev is missing...."	
#  sudo apt-get install $PYDEV  # for python3.x installs
#fi		

mkdir -p build
pushd build

if [[ ! $(find /usr -name "gempyreConfig.cmake") ]]; then
  git clone https://github.com/mmertama/Gempyre.git
  pushd Gempyre
  ./linux_install.sh
  popd
fi

cmake CMakeLists.txt
cmake --build . --config Release
OS_VER_LONG=$(defaults read loginwindow SystemVersionStampAsString)
OS_VER=$(echo "${OS_VER_LONG}" | grep -o '[0-9]\+.[0-9]\+')
PY_VER_LONG=$(python3 --version)
PY_VER=$(echo "${PY_VER_LONG}" | grep -o '[0-9]\+.[0-9]\+')
cp *.so build/lib.macosx-${OS_VER}-x86_64-${PY_VER}
pip3 install -e . --user
