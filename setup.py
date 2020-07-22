from setuptools import setup, find_packages

install_requires=[
        'pyyaml',
        'h5py',
        'matplotlib',
        'Shapely',
        'numpy',
        'pytest']

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="submodule_utils",
    version="0.0.1",
    author="AIM Lab",
    author_email="colinc@fastmail.com",
    description="Submodule for Utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
    python_requires='>=3.6',
)
