from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cleandb",
    version="0.1.0",
    author="EmiliaPanciu",
    description="A utility to empty and clean databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EmiliaPanciu/CleanDB",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "sqlite": [],
        "postgresql": ["psycopg2-binary"],
        "mysql": ["mysql-connector-python"],
    },
    entry_points={
        "console_scripts": [
            "cleandb=cleandb.cli:main",
        ],
    },
)
