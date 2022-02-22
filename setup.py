import os
import pathlib
from setuptools import setup, find_packages

# Package meta-data.
NAME = "greenponik-ble"
DESCRIPTION = "Bluetooth BLE python server"
URL = "https://github.com/GreenPonik/GreenPonik_BLE"
EMAIL = "contact@greenponik.com"
AUTHOR = "GreenPonik SAS"
REQUIRES_PYTHON = ">=3.7.0"

# What packages are required for this module to be executed?
REQUIRED = [
    # 'requests', 'maya', 'records',
    'Adafruit-PlatformDetect'
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Load the package's version.py module as a dictionary.
from version import __version__

setup(
    name=NAME,
    version=__version__,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    license="MIT",
    install_requires=REQUIRED,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=("docs")),
    python_requires=REQUIRES_PYTHON,
    project_urls={  # Optional
        "Source": "https://github.com/GreenPonik/GreenPonik_BLE/",
        "Bug Reports": "https://github.com/GreenPonik/GreenPonik_BLE/issues",
    },
    keywords="GreenPonik hydroponics bluetooth \
        BLE python hardware diy iot raspberry pi",
)
