import random
from math import factorial


def rand_comb(seq):
    """
    Select a random combination, based on Robert Floyd's algorithm
    https://stackoverflow.com/a/2394292/
    """

    # First, randomly select M
    N = len(seq)
    N_range = range(1, N + 1)
    M = random.choices(N_range, weights=[n_combinations(N, r) for r in N_range])[0]

    s = set()
    for j in range(N - M, N):
        t = random.randint(0, j)
        if t in s:
            s.add(j)
        else:
            s.add(t)
    return s


def n_combinations(n, r):
    return factorial(n) // (factorial(r) * factorial(n - r))


# TODO: combinations & permutations
# TODO: correct opt order
# TODO: split to analysis & transformation passes
ALL_OPTS = "aa adce alignment-from-assumptions argpromotion basicaa bdce block-freq branch-prob called-value-propagation callsite-splitting constmerge correlated-propagation deadargelim demanded-bits div-rem-pairs domtree dse early-cse early-cse-memssa elim-avail-extern float2int functionattrs globaldce globalopt globals-aa gvn indvars inferattrs inline instcombine instsimplify ipsccp jump-threading lazy-block-freq lazy-branch-prob lazy-value-info lcssa lcssa-verification libcalls-shrinkwrap licm loop-accesses loop-deletion loop-distribute loop-idiom loop-load-elim loop-rotate loop-simplify loop-sink loop-unroll loop-unswitch loop-vectorize loops lower-expect mem2reg memcpyopt memdep memoryssa mldst-motion opt-remark-emitter pgo-memop-opt postdomtree prune-eh reassociate rpo-functionattrs scalar-evolution sccp scoped-noalias simplifycfg slp-vectorizer speculative-execution sroa strip-dead-prototypes tailcallelim tbaa".split(
    " "
)
