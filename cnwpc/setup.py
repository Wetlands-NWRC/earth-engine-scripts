from setuptools import setup, find_packages


if __name__ == "__main__":
    setup(
        name="cnwpc",
        version="0.1",
        packages=find_packages(),
        entry_points={
            "console_scripts": [
                "cnwpc = app:main",
            ]
        },
    )
