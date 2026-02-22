from setuptools import setup, find_packages

setup(
    name="HardwareMon",
    version="2.0.3",   # increment with each release
    packages=find_packages(),
    install_requires=[
        "psutil",
        "requests"
    ],
    author="Louis",
    description="A hardware monitoring script",
    url="https://github.com/louisboii747/HardwareMon",
)