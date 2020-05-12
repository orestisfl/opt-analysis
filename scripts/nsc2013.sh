#!/bin/bash
set -e
set -x

runs=200
mkdir -p results

clang-10 --version
clang-10 Deadpool/wbs_aes_nsc2013_variants/target/nosuchcon_2013_whitebox_noenc_generator.c -o /tmp/generator
/tmp/generator
[[ -f wbt_noenc ]]

for opt in 0 1 aa adce alignment-from-assumptions attributor barrier basicaa bdce block-freq branch-prob called-value-propagation deadargelim demanded-bits div-rem-pairs domtree early-cse early-cse-memssa float2int functionattrs globaldce globalopt globals-aa indvars inferattrs instcombine instsimplify ipsccp lazy-block-freq lazy-branch-prob lcssa lcssa-verification libcalls-shrinkwrap licm loop-accesses loop-deletion loop-distribute loop-idiom loop-load-elim loop-rotate loop-simplify loop-sink loop-unroll loop-unswitch loop-vectorize loops lower-constant-intrinsics lower-expect mem2reg memcpyopt memdep memoryssa opt-remark-emitter pgo-memop-opt phi-values postdomtree prune-eh reassociate rpo-functionattrs scalar-evolution sccp scoped-noalias simplifycfg sroa strip-dead-prototypes tbaa transform-warning; do

    clang-10 -"opt-$opt" Deadpool/wbs_aes_nsc2013_variants/target/nosuchcon_2013_whitebox_noenc.c -o /tmp/target

    mkdir out
    cd out
    cp ../wbt_noenc ./
    opt-analysis -j --daredevil --progress --inputs $runs --experiments 30 nsc2013 /tmp/target

    cd ..
    zip -r "results/O-$opt-$runs.zip" out/
    rm -rf out
done
