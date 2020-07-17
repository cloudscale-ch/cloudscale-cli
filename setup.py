#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = []
with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = list(i.rstrip() for i in f.readlines())

extras_require = {
    'highlight': ['pygments'],
}

tests_require = []
with open("requirements.dev.txt", "r", encoding="utf-8") as f:
    tests_require = list(i.rstrip() for i in f.readlines())

version = {}
with open("cloudscale_cli/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="cloudscale-cli",
    version=version['__version__'],
    author="René Moser",
    author_email="mail@renemoser.net",
    license="MIT",
    description="Command line interface client for cloudscale.ch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cloudscale-ch/cloudscale-cli",
    packages=find_packages(exclude=["test.*", "tests"]),
    classifiers=[
        "Intended Audience :: System Administrators",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=tests_require,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'cloudscale = cloudscale_cli.cli:cli',
        ],
    },
)
