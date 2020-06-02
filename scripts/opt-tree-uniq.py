#!/usr/bin/env python3
import os
from itertools import combinations
from multiprocessing import Pool, cpu_count
from subprocess import CalledProcessError, check_output, run

from termcolor import colored

ALL_OPTS = "aa adce alignment-from-assumptions argpromotion basicaa bdce block-freq branch-prob called-value-propagation callsite-splitting constmerge correlated-propagation deadargelim demanded-bits div-rem-pairs domtree dse early-cse early-cse-memssa elim-avail-extern float2int functionattrs globaldce globalopt globals-aa gvn indvars inferattrs inline instcombine instsimplify ipsccp jump-threading lazy-block-freq lazy-branch-prob lazy-value-info lcssa lcssa-verification libcalls-shrinkwrap licm loop-accesses loop-deletion loop-distribute loop-idiom loop-load-elim loop-rotate loop-simplify loop-sink loop-unroll loop-unswitch loop-vectorize loops lower-expect mem2reg memcpyopt memdep memoryssa mldst-motion opt-remark-emitter pgo-memop-opt postdomtree prune-eh reassociate rpo-functionattrs scalar-evolution sccp scoped-noalias simplifycfg slp-vectorizer speculative-execution sroa strip-dead-prototypes tailcallelim tbaa".split(
    " "
)


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

    def exec(self):
        return (
            check_output(["timeout", "5", "./" + self.fname + ".out"]).decode().strip()
        )

    def __eq__(self, other):
        return self._md5 == other._md5

    def __hash__(self):
        return self._md5

    def __str__(self):
        return f"{self.fname} -- {' '.join(self.opts)}"


def main(fname):
    # Add both the original bitcode and its optimization without any extra flags
    result = Bitcode(fname)
    results = {result}
    expected = result.exec()
    add_result(call_opt(1, fname, []), results, expected)

    # Out of all possible flags, which produce a unique transformation?
    idx_start = 2
    opts = []
    for opt in ALL_OPTS:
        result = call_opt(idx_start, fname, [opt])
        if add_result(result, results, expected):
            opts.append(opt)
        result.clean()
        idx_start += 1

    with Pool(cpu_count() + 1) as p:
        for r in range(1, len(opts) + 1):
            args = [
                (idx, fname, curr_opts)
                for idx, curr_opts in enumerate(combinations(opts, r), start=idx_start)
            ]
            idx_start += len(args)

            for result in filter(None, p.imap_unordered(call_opt_worker, args)):
                add_result(result, results, expected)
                result.clean()


def add_result(result, results, expected):
    if result in results:
        print(colored("Skip: " + str(result), "red"))
        return False

    if result.exec() != expected:
        raise RuntimeError(f"{result} differs!")

    print(colored("Done: " + str(result), "green"))
    results.add(result)
    return True


def call_opt_worker(args):
    return call_opt(*args)


def call_opt(num, fname, opts):
    out = f"{num}.bc"
    try:
        run(
            ["opt", "-strip", fname, "-o", out] + [f"-{opt}" for opt in opts],
            check=True,
        )
        return Bitcode(out, opts)
    except CalledProcessError as e:
        print("Exception:", e.__dict__)


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
