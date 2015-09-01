#!/bin/zsh

# Compile included AppleScripts

rootdir="$( dirname "$( cd "$( dirname "$0:A" )" && pwd )" )"
# echo "\$rootdir = $rootdir"
scriptdir="${rootdir}/src/scripts"

cd "${scriptdir}"
for script in *.applescript; do
    base=$(basename -s .applescript "${script}")
    destname="${base}.scpt"
    echo "$script -> $destname"
    osacompile -o "${destname}" "${script}"
done
cd -
