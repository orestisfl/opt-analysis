#!/bin/bash
set -e
set -x

[[ -z "$1" ]] && exit 1

mkdir "$1"
cd "$1"

csmith -o "$1.c"

clang-10 --version
# Create the bitcode of the file to be optimized
clang-10 -c -emit-llvm -O0 -Xclang -disable-O0-optnone -I /csmith/runtime "$1.c" -o base.bc

../scripts/opt-tree-uniq.py base.bc

find . -name '*.out' -exec {} \; | sort | uniq > all.stdout
