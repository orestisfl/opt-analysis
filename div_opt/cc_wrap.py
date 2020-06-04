#!/usr/bin/env python3
import subprocess

from div_opt.utils import ALL_OPTS, rand_comb


def main(args):
    assert len(args) > 0

    if "-c" not in args or "-o" not in args:
        _clang(args)
        return

    # Remove optimization flags, we want to control this
    args = [x for x in args if not x.startswith("-O")]

    target_idx = args.index("-o") + 1
    args[target_idx] += ".bc.before_opt"
    _clang(args + ["-emit-llvm"])

    # Opt workflow:
    src = args[target_idx]
    args[target_idx] = args[target_idx].rstrip(".before_opt")
    optimized_bitcode = args[target_idx]

    opts = ["-" + ALL_OPTS[opt] for opt in rand_comb(ALL_OPTS)]
    opt_args = ["opt", src, "-o", optimized_bitcode] + opts
    print("opt args:", opt_args)
    print(subprocess.run(opt_args, check=True))

    args[target_idx] = args[target_idx].rstrip(".bc")
    # args = [x for idx, x in enumerate(args) if x.startswith('-') or idx == target_idx]
    args = list(filter_arguments(args, target_idx))

    # Normal workflow: just call clang with original arguments
    _clang(args + [optimized_bitcode])


def filter_arguments(args, target_idx):
    """
    Create the argument list for the new clang call.
    Removes old sources (now single source should be the optimized bitcode) and
    inapplicable flags.
    """
    for idx, arg in enumerate(args):
        if arg.startswith("-M") or arg.startswith("-I"):
            continue
            # yield arg
            # yield args[idx+1]
        elif arg.startswith("-"):
            yield arg
        elif idx == target_idx:
            yield arg


def _clang(args):
    print("clang args:", args)
    return subprocess.run(["clang"] + args, check=True)


def entry_point():
    import sys

    main(sys.argv[1:])


if __name__ == "__main__":
    entry_point()
