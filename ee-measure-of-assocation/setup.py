from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="moa",
        version="0.0.1",
        description="Simple package that provides functionality for doing moa analysis",
        author="Ryan Hamilton",
        author_email="ryan.hamilton@ec.gc.ca",
        requires=["pandas", "matplotlib"],
        packages=find_packages(include=["moa", "moa.*"]),
    )
