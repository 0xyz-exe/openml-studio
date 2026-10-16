from setuptools import setup, find_packages

setup(
    name="openml-studio",
    version="0.1.0",
    description="Python SDK for OpenML Studio experiment tracking",
    author="OpenML Studio",
    py_modules=["openml_studio"],
    install_requires=[
        "requests>=2.31.0",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.10",
    ],
)
