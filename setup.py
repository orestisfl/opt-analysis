from sys import version_info

from setuptools import setup

common = dict(
    author="Orestis Floros",
    author_email="forestis@kth.se",
    # long_description=readme(),
    version="0.0.1",
)

if version_info >= (3, 0):
    setup(
        name="div-opt",
        packages=["div_opt"],
        entry_points={
            "console_scripts": [
                "cc-wrap = div_opt.cc_wrap:entry_point",
                "opt-tree-uniq = div_opt.opt_tree_uniq:entry_point",
            ]
        },
        **common
    )
else:
    setup(
        name="opt-analysis",
        packages=["opt_analysis"],
        entry_points={
            "console_scripts": [
                "opt-analysis = opt_analysis.main:entry_point",
                "key-check = opt_analysis.daredevil:entry_point",
            ]
        },
        **common
    )
