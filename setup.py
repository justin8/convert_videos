#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="convert_videos",
    version="1.2.13",
    author="Justin Dray",
    author_email="justin@dray.be",
    url="https://github.com/justin8/convert_videos",
    description="This tool accepts a folder and converts any videos that are not already in x265/HEVC format.",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "colorama",
        "ffmpy",
        "video_utils",
    ],
    tests_require=[
        "nose",
        "coverage",
        "mock",
    ],
    test_suite="nose.collector",
    entry_points={
        "console_scripts": [
            "convert-videos=convert_videos:main",
            "convert_videos=convert_videos:main",
            ],
        },
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
    ],
)
