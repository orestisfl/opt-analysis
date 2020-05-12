#!/usr/bin/env python2
import argparse
import os
import subprocess
from contextlib import closing
from glob import glob
from multiprocessing import Pool, cpu_count

from . import daredevil
from .deadpool_dca import TracerGrind, bin2daredevil
from .targets import BIN2DAREDEVIL, CONFIGS, TARGETS


def entry_point():
    """
    Default cli entry point
    """
    import sys

    main(parse_args(sys.argv[1:]))


def parse_args(args):
    """
    Parse args from given list
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--jobs",
        "-j",
        help="Number of parallel jobs",
        default=None,
        type=int,
        nargs="?",
        const=-1,
    )
    parser.add_argument(
        "--inputs",
        help=(
            "Number of random inputs to process with the whitebox."
            "This leads to an equivalent number of runs per experiment."
        ),
        metavar="NUM",
        type=int,
        default=200,
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode for TracerGrind"
    )
    parser.add_argument(
        "--experiments",
        help="Number of times to repeat the experiment",
        metavar="NUM",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--daredevil",
        action="store_true",
        help="Run daredevil from produced configuration",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        dest="iterator",
        help="Show progress bar. Requires tqdm and --expirements > 1.",
    )
    parser.add_argument(
        "target", help="One of the possible whitebox targets", choices=TARGETS.keys(),
    )
    parser.add_argument(
        "executable", help="Path to executable that implements the whitebox"
    )

    args = parser.parse_args(args)

    if args.experiments > 1 and not args.daredevil:
        raise ValueError("--expirements requires --daredevil")

    if args.jobs is None:
        args.jobs = 0
    elif args.jobs <= 0:
        args.jobs = cpu_count()

    return args


def main(args):
    """
    Run main process with parsed arguments
    """
    _rm_f("score.txt")

    target_config = CONFIGS[args.target]
    for experiment_idx in _experiments_iterator(args):
        if args.jobs > 1:
            with closing(Pool(args.jobs)) as p:
                p.map(_exec, [(n, args) for n in _divide_runs(args.inputs, args.jobs)])
        else:
            _exec((args.inputs, args))
        bin2daredevil(config=BIN2DAREDEVIL[args.target])

        if not args.daredevil:
            continue

        latest_file = max(
            (x for x in glob("*.config") if target_config in x), key=os.path.getctime
        )
        daredevil_output = subprocess.check_output(["daredevil", "-c", latest_file])
        with open("daredevil-%d.log" % experiment_idx, "w") as f:
            f.write(daredevil_output.strip() + "\n")
        with open("score.txt", "a") as f:
            f.write(
                daredevil.parse_lines(daredevil_output.split("\n"), target=args.target)
                + "\n"
            )


def _experiments_iterator(args):
    r = range(args.experiments)
    if args.iterator and args.experiments > 1:
        from tqdm import tqdm

        return tqdm(r)
    return r


def _divide_runs(runs, processes):
    """
    Splits a certain amount of runs among proncesses as evenly as possible.

    >>> _divide_runs(1000, 4)
    [250, 250, 250, 250]
    >>> _divide_runs(5, 10)
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
    >>> _divide_runs(5, 2)
    [3, 2]
    """
    quotient, remainder = divmod(runs, processes)
    return [quotient + 1] * remainder + [quotient] * (processes - remainder)


def _exec(args):
    runs, args = args
    processinput, processoutput = TARGETS[args.target]
    t = TracerGrind(
        args.executable,
        processinput=processinput,
        processoutput=processoutput,
        addr_range="0x108000-0x3ffffff",
        debug=args.debug,
    )
    t.run(runs, verbose=args.debug)


def _rm_f(fname):
    try:
        os.remove(fname)
    except OSError:
        pass


if __name__ == "__main__":
    entry_point()
