#!/bin/bash

set -e

# "Linux" binary is not supported in pypi

targets=( "Windows" "MacOS" )

rm -rf dist
mkdir -p dist


REL=$(curl -Ls -o /dev/null -w %{url_effective}  https://github.com/mmertama/Gempyre-Python/releases/latest | grep -o "[^/]*$")

for value in "${targets[@]}"; do
    ARCH=gempyre-py-$REL-$value.tar.gz
    wget "https://github.com/mmertama/Gempyre-Python/releases/download/$REL/$ARCH"
    tar -xzvf $ARCH
    rm $ARCH
done

USER=__token__
PASS=$(cat $1)

twine upload dist/* -u $USER -p $PASS 

