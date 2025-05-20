"""
Setup script for the Bangladesh Energy Transition simulation package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="bangladesh_energy",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simulation model for Bangladesh's renewable energy transition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bangladesh-energy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bangladesh-energy=bangladesh_energy.run_simulation:main",
        ],
    },
) 