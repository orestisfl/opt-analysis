#!/usr/bin/env python3
import os
import shlex
from argparse import ArgumentParser, Namespace
from itertools import combinations
from multiprocessing import Pool, cpu_count
from subprocess import CalledProcessError, check_output, run
from typing import Iterable, Optional, Set

from div_opt.utils import ALL_OPTS
from termcolor import colored


def parse_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument(
        "--exec",
        "-e",
        nargs="?",
        const="",
        default=None,
        help="Try to run produced executable, compare its output",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Always clean produced files after being done with them",
    )
    parser.add_argument("fname", help="Starting point, must be an LLVM bitcode file")
    return parser.parse_args()


class Bitcode:
    def __init__(self, fname: str, current_opts: Optional[Iterable[str]]) -> None:
        self.opts = current_opts
        self.fname, ext = os.path.splitext(fname)
        assert ext == ".bc"

        exec_fname = self.fname + ".out"
        run(["clang", fname, "-o", exec_fname], check=True)
        self._md5 = int(check_output(["md5sum", exec_fname]).decode().split()[0], 16,)
        # self._md5 = int(check_output(["md5sum", fname]).decode().split()[0], 16)

    def clean(self) -> None:
        os.remove(self.fname + ".bc")
        os.remove(self.fname + ".out")

    def exec(self, exec_args: Optional[str]) -> Optional[str]:
        if exec_args is None:
            return None

        exec_args = shlex.split(exec_args)
        return (
            check_output(["timeout", "20", "./" + self.fname + ".out"] + exec_args)
            .decode()
            .strip()
        )

    def __eq__(self, other: "Bitcode") -> bool:
        return self._md5 == other._md5

    def __hash__(self) -> int:
        return self._md5

    def __str__(self) -> str:
        return f"{self.fname} -- {' '.join(self.opts)}"


def main(args: Namespace) -> None:
    # Add both the original bitcode and its optimization without any extra flags
    result = Bitcode(args.fname, None)
    results = {result}
    expected = result.exec(args.exec)
    add_result(call_opt(1, args.fname, []), results, args.exec, expected)

    # Out of all possible flags, which produce a unique transformation?
    idx_start = 2
    opts = []
    for opt in ALL_OPTS:
        result = call_opt(idx_start, args.fname, [opt])
        if add_result(result, results, args.exec, expected):
            opts.append(opt)
        result.clean()
        idx_start += 1

    with Pool(cpu_count() + 1) as p:
        for r in range(1, len(opts) + 1):
            call_args = [
                (idx, args.fname, curr_opts)
                for idx, curr_opts in enumerate(combinations(opts, r), start=idx_start)
            ]
            idx_start += len(call_args)

            for result in filter(None, p.imap_unordered(call_opt_worker, call_args)):
                if not add_result(result, results, args.exec, expected) or args.clean:
                    result.clean()


def add_result(
    result: Bitcode,
    results: Set[Bitcode],
    exec_args: Optional[str],
    expected: Optional[str],
) -> bool:
    if result in results:
        print(colored("Skip: " + str(result), "red"))
        return False

    if result.exec(exec_args) != expected:
        raise RuntimeError(f"{result} differs!")

    print(colored("Done: " + str(result), "green"))
    results.add(result)
    return True


def call_opt_worker(args: Iterable) -> Bitcode:
    return call_opt(*args)


def call_opt(num: int, fname: str, opts: Optional[Iterable[str]]) -> Bitcode:
    out = f"{num}.bc"
    try:
        run(
            ["opt", "-strip", fname, "-o", out] + [f"-{opt}" for opt in opts],
            check=True,
        )
        return Bitcode(out, opts)
    except CalledProcessError as e:
        print("Exception:", e.__dict__)


def entry_point() -> None:
    main(parse_args())


if __name__ == "__main__":
    entry_point()
