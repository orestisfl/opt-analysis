#!/bin/bash
set -e
set -x

# XXX: could be $1, $2, …
[[ -z $OPT_TO_USE ]] && exit 1
[[ -z $OPT_BATCH ]] && exit 1
[[ -z $OPT_RUNS ]] && exit 1

experiments=25
mkdir -p results

clang-10 --version
clang-10 Deadpool/wbs_aes_nsc2013_variants/target/nosuchcon_2013_whitebox_noenc_generator.c -o /tmp/generator
/tmp/generator
[[ -f wbt_noenc ]]

# Create the bitcode of the file to be optimized
clang-10 -c -emit-llvm -O0 -Xclang -disable-O0-optnone Deadpool/wbs_aes_nsc2013_variants/target/nosuchcon_2013_whitebox_noenc.c -o /tmp/base.bc

# Optimize the base bitcode with the current optimization flag.
eval opt-10 "-$OPT_TO_USE" /tmp/base.bc -o /tmp/tmp.bc
clang-10 /tmp/tmp.bc -o /tmp/target

mkdir out
cd out
cp ../wbt_noenc ./
opt-analysis -j --daredevil --progress --inputs $OPT_RUNS --experiments $experiments nsc2013 /tmp/target

cd ..
zip -r "results/$OPT_BATCH.O-$OPT_TO_USE-$experiments-$OPT_RUNS.zip" out/
