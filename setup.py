from setuptools import setup, find_packages

setup(
    name="clight",
    version="0.8",
    packages=find_packages(),
    install_requires=[
        "Click",
        "pychromecast",
        "phue",
        "parsec",
    ],
    entry_points={
        "console_scripts": [
            "clight=clight.main:cli",
        ]
    },
)
