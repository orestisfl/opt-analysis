#!/usr/bin/env python3
import os
from itertools import combinations
from subprocess import check_output, run

from termcolor import colored
from tqdm import tqdm

ALL_OPTS = "aa adce alignment-from-assumptions argpromotion basicaa bdce block-freq branch-prob called-value-propagation callsite-splitting constmerge correlated-propagation deadargelim demanded-bits div-rem-pairs domtree dse early-cse early-cse-memssa elim-avail-extern float2int functionattrs globaldce globalopt globals-aa gvn indvars inferattrs inline instcombine instsimplify ipsccp jump-threading lazy-block-freq lazy-branch-prob lazy-value-info lcssa lcssa-verification libcalls-shrinkwrap licm loop-accesses loop-deletion loop-distribute loop-idiom loop-load-elim loop-rotate loop-simplify loop-sink loop-unroll loop-unswitch loop-vectorize loops lower-expect mem2reg memcpyopt memdep memoryssa mldst-motion opt-remark-emitter pgo-memop-opt postdomtree prune-eh reassociate rpo-functionattrs scalar-evolution sccp scoped-noalias simplifycfg slp-vectorizer speculative-execution sroa strip-dead-prototypes tailcallelim tbaa".split(
    " "
)
num = 0


class Bitcode:
    def __init__(self, fname, current_opts=tuple()):
        self.opts = current_opts
        self.fname, ext = os.path.splitext(fname)
        assert ext == ".bc"

        exec_fname = self.fname + ".out"
        run(["clang", fname, "-o", exec_fname], check=True)
        self._md5 = int(check_output(["md5sum", exec_fname]).decode().split()[0], 16,)
        # self._md5 = int(check_output(["md5sum", fname]).decode().split()[0], 16)

    def clean(self):
        os.remove(self.fname + ".bc")
        os.remove(self.fname + ".out")

    def __eq__(self, other):
        return self._md5 == other._md5

    def __hash__(self):
        return self._md5

    def __str__(self):
        return f"{self.fname} -- {' '.join(self.opts)}"


def main(fname):
    # Add both the original bitcode and its optimization without any extra flags
    results = {Bitcode(fname)}
    uniq_opt(fname, [], results)

    # Out of all possible flags, which produce a unique transformation?
    opts = []
    for opt in tqdm(ALL_OPTS, desc="Filter all opts"):
        result = uniq_opt(fname, [opt], results)
        if result is not None:
            opts.append(opt)

    for r in tqdm(range(1, len(opts) + 1)):
        for curr_opts in combinations(opts, r):
            uniq_opt(fname, curr_opts, results)


def uniq_opt(fname, opts, results):
    result = call_opt(fname, opts)

    if result is None:
        return None
    if result in results:
        tqdm.write(colored("Skip: " + str(result), "red"))
        result.clean()
        return None
    tqdm.write(colored("Done: " + str(result), "green"))
    results.add(result)
    return result


def call_opt(fname, opts):
    global num
    num += 1

    out = f"{num}.bc"
    run(
        ["opt", "-strip", fname, "-o", out] + [f"-{opt}" for opt in opts], check=True,
    )
    return Bitcode(out, opts)


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
