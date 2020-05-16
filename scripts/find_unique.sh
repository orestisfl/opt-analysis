#!/bin/bash
set -e
set -x

clang-10 --version 1>&2

# Create the bitcode of the file to be optimized
clang-10 -c -emit-llvm -O0 -Xclang -disable-O0-optnone Deadpool/wbs_aes_nsc2013_variants/target/nosuchcon_2013_whitebox_noenc.c -o /tmp/base.bc
rm -rf /tmp/bitcode_history
mkdir /tmp/bitcode_history

printf '['

for opt in O0 O1 O2 O3 Os Oz aa adce alignment-from-assumptions argpromotion basicaa bdce block-freq branch-prob called-value-propagation callsite-splitting constmerge correlated-propagation deadargelim demanded-bits div-rem-pairs domtree dse early-cse early-cse-memssa elim-avail-extern float2int functionattrs globaldce globalopt globals-aa gvn indvars inferattrs inline instcombine instsimplify ipsccp jump-threading lazy-block-freq lazy-branch-prob lazy-value-info lcssa lcssa-verification libcalls-shrinkwrap licm loop-accesses loop-deletion loop-distribute loop-idiom loop-load-elim loop-rotate loop-simplify loop-sink loop-unroll loop-unswitch loop-vectorize loops lower-expect mem2reg memcpyopt memdep memoryssa mldst-motion opt-remark-emitter pgo-memop-opt postdomtree prune-eh reassociate rpo-functionattrs scalar-evolution sccp scoped-noalias simplifycfg slp-vectorizer speculative-execution sroa strip-dead-prototypes tailcallelim tbaa; do
  # Optimize the base bitcode with the current optimization flag.
  opt-10 "-$opt" /tmp/base.bc -o tmp.bc
  for fname in /tmp/bitcode_history/*.bc; do
    # Compare all past optimized bitcodes to find any identical ones &
    # avoid re-running the same analysis.
    if cmp --silent tmp.bc "$fname"; then
      rm tmp.bc
    fi
  done

  [[ -f tmp.bc ]] || continue
  mv tmp.bc "/tmp/bitcode_history/$opt.bc"

  printf "$opt,"
done
echo ']'
