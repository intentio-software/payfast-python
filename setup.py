from setuptools import setup, find_packages

setup(
    name="payfast",
    version="0.1.2",
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
