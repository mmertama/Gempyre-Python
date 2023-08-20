#!/bin/bash

set -e

targets=( "Linux" "Windows" "MacOS" )

rm -rf dist
mkdir -p dist

REL=$(curl -Ls -o /dev/null -w %{url_effective}  https://github.com/mmertama/Gempyre-Python/releases/latest | grep -o "[^/]*$")

for value in "${targets[@]}"; do
    echo "https://github.com/mmertama/Gempyre-Python/releases/download/$REL/$value.tar.gz"
done
