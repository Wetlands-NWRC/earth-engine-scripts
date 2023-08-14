import os
import ee
import eeng

from dataclasses import dataclass
from typing import List

from eeng.server.calc import *
from eeng.server.models import RandomForestModel
from eeng.server.filters import BoxCar
from eeng.server.collections import ImageCollectionIDs


@dataclass
class PreprocessingOutput:
    img: ee.Image
    training_data: ee.FeatureCollection
    lookup: ee.Dictionary


@dataclass
class ProcessingOutput:
    pass


def preprocessing(
    aoi: ee.Geometry, s1: List[str], s2: str, terrain: str, fourier: str
) -> PreprocessingOutput:
    # Sentinel - 1
    spring = ()
    summer = ()
    bxcr = BoxCar(1)
    ratio = Ratio()
    s1_col = ee.ImageCollection(s1).filterBounds(aoi).map(bxcr).map(ratio)

    s1_spri = s1_col.filter(ee.Filter.dayOfYear(spring[0], spring[1])).mosaic()
    s1_summ = s1_col.filter(ee.Filter.dayOfYear(summer[0], summer[1])).mosaic()

    s1_img = ee.Image.cat(s1_spri, s1_summ)

    # Sentinel - 2
    # remove all non spectral bands
    s2_col = ee.ImageCollection(s2).filterBounds(aoi).select("")
    # create the create the calculators
    # NDVI
    spri_ndvi = NDVI()
    spri_ndvi.nir = None
    spri_ndvi.red = None
    summ_ndvi = NDVI()
    summ_ndvi.nir = None
    summ_ndvi.red = None
    fall_ndvi = NDVI()
    fall_ndvi.nir = None
    fall_ndvi.red = None

    # SAVI
    spri_savi = SAVI()
    spri_savi.nir = None
    spri_savi.red = None
    summ_savi = SAVI()
    summ_savi.nir = None
    summ_savi.red = None
    fall_savi = SAVI()
    fall_savi.nir = None
    fall_savi.red = None

    # TASSLED CAP
    spri_tcap = TasselCap()
    summ_tcap = TasselCap()
    fall_tcap = TasselCap()

    # map the calculators
    s2_col = (
        s2_col.map(spri_ndvi)
        .map(summ_ndvi)
        .map(fall_ndvi)
        .map(spri_savi)
        .map(summ_savi)
        .map(fall_savi)
        .map(spri_tcap)
        .map(summ_tcap)
        .map(fall_tcap)
    )

    # remove 60m bands

    alos_img = (
        ee.ImageCollection(ImageCollectionIDs.alos)
        .filterDate("2019", "2020")
        .map(bxcr)
        .map(ratio)
        .first()
    )

    ter_col_img = ee.ImageCollection(terrain).filterBounds(aoi).mosaic()
    four_col_img = ee.ImageCollection(fourier).filterBounds(aoi).mosaic()

    # merge all the images
    img = ee.Image.cat(s1_img, s2_col, alos_img, ter_col_img, four_col_img).clip(aoi)

    # prep the training data
    training_data = (
        ee.FeatureCollection("").addXCoordinate().addYCoordinate().generateSamples(img)
    )
    lookup = training_data.getLookup("Wetland", sorted=True)

    training_data = training_data.remap(lookup.keys(), lookup.values(), "Wetland")

    return PreprocessingOutput(img, training_data, lookup)


def processing(img: ee.Image, training_data: ee.FeatureCollection) -> ee.Image:
    rf_model = (
        RandomForestModel()
        .fit(training_data, classProperty="Wetland", inputProperties=img.bandNames())
        .apply(img)
    )
    return rf_model


def postprocessing(img: ee.Image):
    """Handles creating the jobs that will be sent to the server"""


def main():
    pass


if __name__ == "__main__":
    main()
