from setuptools import setup, find_packages

setup(
    name="clight",
    version="0.3.2",
    packages=find_packages(),
    install_requires=[
        "Click",
        "pychromecast",
    ],
    entry_points={
        "console_scripts": [
            "clight=clight.main:cli",
        ]
    },
)
