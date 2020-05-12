from setuptools import find_packages, setup

setup(
    name="opt-analysis",
    author="Orestis Floros",
    author_email="forestis@kth.se",
    # url="https://github.com/kth-tcs/llvm-paraphrasing",
    # long_description=readme(),
    version="0.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "opt-analysis = opt_analysis.main:entry_point",
            "key-check = opt_analysis.daredevil:entry_point",
        ]
    },
)
