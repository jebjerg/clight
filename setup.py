from setuptools import setup

setup(
    name="clight",
    version="0.2",
    py_modules=["main", "homeassistant_api", "config"],
    install_requires=[
        "Click",
        "pychromecast",
    ],
    entry_points="""
        [console_scripts]
        clight=main:cli
    """,
)
