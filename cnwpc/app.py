from pathlib import Path
from osgeo import gdal
import os
import re

import sys

from eeng.client.assessment import confusion_matrix_from_file


"""
A Purpose built applitcation to build the output files from the EENG application. 
"""


def build_rasters(root: str):
    filenames = []
    for root, dirs, files in os.walk(root):
        for file in files:
            if file.endswith(".tif"):
                filenames.append(os.path.join(root, file))

    regions = set([re.findall(r"\b\d{3}\b", filename)[0] for filename in filenames])

    for region in regions:
        region_files = []
        for filename in filenames:
            if region == filename.split("\\")[-3]:
                region_files.append(filename)
        outputdir = Path(region_files[0]).parent
        print("building raster for region: ", region)
        print("Location: ", outputdir)
        print("building vrt ...")
        vrt = gdal.BuildVRT(os.path.join(outputdir, f"vrt_{region}.vrt"), region_files)
        print("building classification raster ...")
        gdal.Translate(os.path.join(outputdir, f"classification_{region}.tif"), vrt)
        vrt = None
        print("GeoTIFF created", end="\n\n")
        region_files = None


def build_matrix(root: str):
    filenames = []
    for root, dirs, files in os.walk(root):
        for file in files:
            if file.endswith(".geojson") and "assessment" in os.path.basename(file):
                filenames.append(os.path.join(root, file))

    regions = set([re.findall(r"\b\d{3}\b", filename)[0] for filename in filenames])

    for region in regions:
        region_files = []
        for filename in filenames:
            if region == filename.split("\\")[-3]:
                outputdir = Path(filename).parent
                cfm = confusion_matrix_from_file(filename)
                cfm.to_csv(os.path.join(outputdir, f"confusion_matrix_{region}.csv"))


def main():
    if len(sys.argv) < 2:
        raise ValueError("root path not provided")
    root = sys.argv[1]
    if not os.path.exists(root):
        raise ValueError("root path does not exist")
    elif not os.path.isdir(root):
        raise ValueError("root path is not a directory")
    build_matrix(root)
    build_rasters(root)
