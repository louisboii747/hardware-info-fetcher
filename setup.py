from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hardwaremon",
    version="2.5.0",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "requests",
        # other deps
    ],
    entry_points={
        "console_scripts": [
            "hardwaremon=hardwaremon.main:main"
        ]
    },
    author="Louis",
    description="Hardware monitoring tool for Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/louisboii747/HardwareMon",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)