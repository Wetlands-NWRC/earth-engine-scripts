import os
import ee

from dataclasses import dataclass

from eeng.server.tables import TrainingPoints
from eeng.server.classifiers import RandomForestClassification

from eeng.server.toolboxs.cnwi.builders import *

import inputs


@dataclass
class Payload:
    s1 = None
    s2 = None
    fourier = None
    terrain = None
    training = None
    validation = None
    region = None


class StackBuilder:
    def __init__(self) -> None:
        self._images = []
        self.stack = None

    def addImage(self, image: ee.Image):
        self._images.append(image)
        return self

    def build(self):
        self.stack = ee.Image.cat(self._images)
        return self


def build_stack(aoi: ee.Geometry):
    # build inputs
    s1builder = Sentinel1Builder()
    s1builder.collection = ee.ImageCollection(Payload.s1)

    s1builder.addSpatialFilter(aoi).addBoxCar().addRatio().build()

    s1_spring = s1builder.collection.filter(ee.Filter.dayOfYear(80, 172)).mosaic()
    s1_summer = s1builder.collection.filter(ee.Filter.dayOfYear(173, 265)).mosaic()

    data_cube_builder = DataCubeBuilder()
    data_cube_builder.collection = ee.ImageCollection(Payload.s2)
    data_cube_builder.addSpatialFilter(aoi).addNDVI().addSAVI().addTasselCap().build()

    dc_proc_col = data_cube_builder.collection

    ftbldr = FourierBuilder()
    ftbldr.collection = ee.ImageCollection(Payload.fourier)
    ftbldr.addSpatialFilter(aoi).build()
    fourier = ftbldr.collection

    trainbldr = TerrainBuilder()
    trainbldr.collection = ee.ImageCollection(Payload.terrain)
    trainbldr.addSpatialFilter(aoi).build()

    terrain = trainbldr.collection

    stackbldr = inputs.StackBuilder()
    stackbldr.addImage(s1_spring).addImage(s1_summer).addImage(dc_proc_col).addImage(
        fourier
    ).addImage(terrain).build()

    stack = stackbldr.stack

    return stack


def build_samples(collection: ee.FeatureCollection, class_prop: str) -> TrainingPoints:
    pnts = TrainingPoints(
        points=collection,
        classProperty=class_prop,
    )

    pnts = pnts.addYCoordinate().addXCoordinate().addValues()

    samples = pnts.generateSamples()
    return samples


def main():
    # ref is the data which we are sampeling and classifying
    # trg is the data which we are predicting on

    # build the ref datasets
    ref_aoi = None
    ref_training = None

    ref_stack = build_stack(ref_aoi)
    ref_samples = build_samples(ref_training, "class_name")

    # build the classifier
    classifier = RandomForestClassification()
    classifier.fit(ref_samples.points, ref_samples.classProperty, ref_stack.bandNames())

    trg_aoi = None
    trg_stack = build_stack(trg_aoi)

    trg_clf = classifier.apply(trg_stack)

    # export Classification

    # export the

    #


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    main()
