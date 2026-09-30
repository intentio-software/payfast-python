from setuptools import setup, find_namespace_packages

try:
    import os

    version = os.getenv("VERSION") or "0.1.4"
except Exception:
    version = "0.1.4"

setup(
    name="payfast",
    version="0.1.3",
    # find_packages() requires an __init__.py to recognize a directory as a
    # package - this repo deliberately has none (payfast/ is an implicit
    # namespace package, see .gitignore), so that call silently returned an
    # empty list and every built wheel shipped zero files. Verified: a real
    # install from this exact source tree raised ModuleNotFoundError even
    # though `pip install` itself reported success.
    packages=find_namespace_packages(include=["payfast", "payfast.*"]),
    author="Max Dittmar",
    author_email="max@intentio.co.za",
    description="Python library for Payfast by network API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/intentio-software/payfast-python",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        # Add more classifiers as needed
    ],
)
