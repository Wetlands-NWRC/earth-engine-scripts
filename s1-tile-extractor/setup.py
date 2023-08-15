from setuptools import setup, find_packages


if __name__ == '__main__':
    setup(
        name='s1_data_extractor',
        version='0.0.1',
        install_requires=[
            "earthengine-api",
            "geopandas",
        ],
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                's1datex = app:main',
            ]
        }
    )