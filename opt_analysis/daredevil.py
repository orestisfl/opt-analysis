#!/usr/bin/env python2
import argparse

from .targets import KEYS


def parse_args(args):
    parser = argparse.ArgumentParser()
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "--target", help="One of the possible whitebox targets", choices=KEYS.keys(),
    )
    target_group.add_argument("--expected")
    args = parser.parse_args(args)
    return args


def parse_lines(lines, target=None, expected=None):
    if target is not None:
        if expected is not None:
            raise ValueError
        expected = KEYS[target].lower()
    if expected is None:
        raise ValueError

    return ":".join(str(cmp_key(key, expected)) for key in parse_daredevil(lines))


def parse_daredevil(lines):
    """
    Extract top 1 key for both methods from daredevil output
    """
    key1 = False
    key2 = False
    for line in lines:
        if key1 or key2:
            yield line.split(":")[-1].strip()
            if key2:
                break
            key1 = False
            continue
        key1 = line.strip() == "Most probable key sum(abs):"
        key2 = line.strip() == "Most probable key max(abs):"


def cmp_key(key, expected):
    assert len(key) == len(expected)
    return sum(
        key[idx : idx + 2] == expected[idx : idx + 2] for idx in range(0, len(key), 2)
    )


def entry_point():
    import sys

    args = parse_args(sys.argv[1:])
    print parse_lines(sys.stdin, **vars(args))


if __name__ == "__main__":
    entry_point()
