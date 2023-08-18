import os
import re
from pathlib import Path

from osgeo import gdal

from eeng.client.assessment import confusion_matrix_from_file


class PostClassificationBuilder:
    def __init__(self, root: str = None) -> None:
        self.root = "." if root is None else root
        self.tifs = []
        self.assessments = []

    def get_tifs(self):
        for root, dir, files in os.walk(self.root):
            for file in files:
                if file.endswith(".tif"):
                    path = os.path.join(root, file)
                    self.tifs.append(path)
        return self

    def get_assessments(self):
        for root, dir, files in os.walk(self.root):
            for file in files:
                if "assessment" in file and file.endswith(".geojson"):
                    path = os.path.join(root, file)
                    self.assessments.append(path)
        return self

    def build_rasters(self) -> None:
        print("building rasters ...")
        for region in self._get_region_ids(self.assessments):
            region_tifs = [tif for tif in self.tifs if region in tif]
            if any(
                [
                    os.path.basename(tif) == f"classification_{region}.tif"
                    for tif in region_tifs
                ]
            ):
                print(
                    f"classification_{region}.tif already exists, skipping ...",
                    end="\n\n",
                )
                continue

            print("building raster for region: ", region)
            partent = Path(region_tifs[0]).parent
            print("exporting to: ", partent)
            print("building vrt ...")
            vrt = gdal.BuildVRT(
                os.path.join(partent, f"tiles_{region}.vrt"), region_tifs
            )
            print("Translating to GeoTIFF ...")
            gdal.Translate(os.path.join(partent, f"classification_{region}.tif"), vrt)
            vrt = None
            print("GeoTIFF created", end="\n\n")
        return self

    def build_assessment(self) -> None:
        for region in self._get_region_ids(self.assessments):
            assessments = [
                assessment for assessment in self.assessments if region in assessment
            ]
            parent = Path(assessments[0]).parent
            print("building assessment for region: ", region)
            matrix = confusion_matrix_from_file(assessments[0])
            print("building confusion matrix ...")
            matrix.to_csv(os.path.join(parent, f"confusion_matrix_{region}.csv"))
        return self

    @staticmethod
    def _get_region_ids(paths: str):
        return set([re.findall(r"\b\d{3}\b", path)[0] for path in paths])


def build_vrt(tifs: list, region_id: str):
    vrt = gdal.BuildVRT("tiles.vrt", tifs)
    gdal.Translate("classification.tif", vrt)
    vrt = None


def main(search_dir: str = None):
    builder = PostClassificationBuilder(search_dir)
    builder.get_tifs()
    builder.get_assessments()
    builder.build_rasters()
    builder.build_assessment()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main(
        r"Y:\Wetlands\CNWI\working\cnwi-pipeline\priority-areas\aoi_NS\output\20230815_104538"
    )
