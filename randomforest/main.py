import ee

from eeng.server.image_collection import Sentinel1Creator, Sentinel2Creator
from eeng.server.classifiers import RandomForestClassifier
from eeng.server.table import TraningPoints
from eeng.server.toolbox.image.NWRCStackingTool


def main():
    

    

    assets = ee.FeatureCollection("")

    trpts = TraniningPoints(asset, 'class_name')

    trpts.addXCoordinate().addYCoordinate()

    sampels = trpts.getSamples()

if __name__ == '__main__':
    main()
