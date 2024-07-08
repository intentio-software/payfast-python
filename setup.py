from setuptools import setup, find_packages

try:
    import os

    version = os.getenv("VERSION") or "0.1.4"
except Exception:
    version = "0.1.4"

setup(
    name="payfast",
    version="0.1.3",
    packages=find_packages(),
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
