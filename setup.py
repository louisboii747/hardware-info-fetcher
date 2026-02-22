from csv import __version__

from setuptools import setup, find_packages

setup(
    name="HardwareMon",
    version="2.0.0",
    packages=find_packages(exclude=["test_hardwaremon*"]),
    install_requires=[
        "psutil",
        "requests",
        # add any other dependencies your project needs
    ],
    entry_points={
        "console_scripts": [
            "hardwaremon=HardwareMon.main:main",  # adjust if your main file is different
        ]
    },
)


setup(
    name="HardwareMon",
    version=__version__,
    packages=find_packages(),
    install_requires=[
        "psutil",
        "requests"
    ],
)