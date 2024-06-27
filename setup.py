from setuptools import setup, find_packages

setup(
    name="payfast",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # List dependencies here
        "requests",
        "pytz",
        "pydantic",
    ],
    # entry_points={
    #     "console_scripts": [
    #         "your_script = your_package.module1:main_function",
    #     ],
    # },
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
