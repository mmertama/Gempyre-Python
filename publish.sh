#!/bin/bash

set -e

# "Linux" binary is not supported in pypi

targets=( "Windows" "MacOS" )

rm -rf dist
mkdir -p dist


REL=$(curl -Ls -o /dev/null -w %{url_effective}  https://github.com/mmertama/Gempyre-Python/releases/latest | grep -o "[^/]*$")

for value in "${targets[@]}"; do
    wget "https://github.com/mmertama/Gempyre-Python/releases/download/$REL/$value.tar.gz"
    tar -xzvf $value.tar.gz
    rm $value.tar.gz
done

USER=__token__
PASS=$(cat $1)

twine upload dist/* -u $USER -p $PASS 

