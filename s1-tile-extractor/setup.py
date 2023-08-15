from setuptools import setup, find_packages


if __name__ == "__main__":
    setup(
        name="s1_tile_extractor",
        version="1.0.0",
        install_requires=[
            "earthengine-api",
            "geopandas",
        ],
        packages=find_packages(),
        entry_points={
            "console_scripts": [
                "s1tilex = app:main",
            ]
        },
    )
