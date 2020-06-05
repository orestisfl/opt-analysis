#!/bin/bash
set -e
set -x

# XXX: could be $1, $2, …
[[ -z $OPT_TO_USE ]] && exit 1
[[ -z $OPT_BATCH ]] && exit 1
[[ -z $OPT_RUNS ]] && exit 1

# https://stackoverflow.com/a/6022431
opts="$(sed "${OPT_TO_USE}q;d" opts.conf)"

experiments=20

clang-10 --version

(
prev="$PWD/Deadpool/wbs_aes_ches2016/target/ches_wb_challenge.tgz"
cd /tmp
tar xf "$prev"

# Create the bitcode of the file to be optimized
clang-10 -c -emit-llvm -O0 -Xclang -disable-O0-optnone chow_aes3_encrypt_wb.c -o base.bc

# Optimize the base bitcode with the current optimization flag.
eval opt-10 "-$opts" base.bc -o tmp.bc
clang-10 challenge.c tmp.bc -o /tmp/target
)

(
mkdir results
mkdir out
cd out
cp ../wbt_noenc ./
opt-analysis -j --daredevil --progress --inputs "$OPT_RUNS" --experiments $experiments ches2016 /tmp/target
)

zip -r "results/$OPT_BATCH.O$OPT_TO_USE-$experiments-$OPT_RUNS.zip" out/
