from eeng.server.calc import *
from eeng.server.filters import BoxCar
from eeng.server.image_collection import Sentinel1
from eeng.server.collections import ImageCollectionIDs
from eeng.server.tables import TrainingPoints


class DataCubeBuilder:
    def __init__(self) -> None:
        self.collection: ee.ImageCollection = None

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        if not isinstance(value, ee.ImageCollection):
            raise TypeError("Input must be an ee.ImageCollection")
        self._collection = value

    def addSpatialFilter(self, geometry: ee.Geometry) -> None:
        """adds a spatial filter to the input collection"""
        self.collection = self.collection.filterBounds(geometry)
        return self

    def addNDVI(self):
        """adds NDVI  to the input collection"""

        spri_ndvi = NDVI(
            nir="a_spri_b08_10m",
            red="a_spri_b04_10m",
        )

        summ_ndvi = NDVI(
            nir="b_summ_b08_10m",
            red="b_summ_b04_10m",
        )

        fall_ndvi = NDVI(
            nir="c_fall_b08_10m",
            red="c_fall_b04_10m",
        )

        self.collection = (
            self.collection.addCalculator(spri_ndvi)
            .addCalculator(summ_ndvi)
            .addCalculator(fall_ndvi)
        )
        return self

    def addSAVI(self):
        """adds SAVI to the input collection"""
        spri_savi = SAVI(
            nir="a_spri_b08_10m",
            red="a_spri_b04_10m",
        )

        summ_savi = SAVI(
            nir="b_summ_b08_10m",
            red="b_summ_b04_10m",
        )
        fall_savi = SAVI(
            nir="c_fall_b08_10m",
            red="c_fall_b04_10m",
        )

        self.collection = (
            self.collection.addCalculator(spri_savi)
            .addCalculator(summ_savi)
            .addCalculator(fall_savi)
        )
        return self

    def addTasselCap(self):
        """adds TasselCap to the input collection"""
        spri_tcap = TasselCap(
            blue="a_spri_b02_10m",
            green="a_spri_b03_10m",
            red="a_spri_b04_10m",
            nir="a_spri_b08_10m",
            swir1="a_spri_b11_20m",
            swir2="a_spri_b12_20m",
        )
        summ_tcap = TasselCap(
            blue="b_summ_b02_10m",
            green="b_summ_b03_10m",
            red="b_summ_b04_10m",
            nir="b_summ_b08_10m",
            swir1="b_summ_b11_20m",
            swir2="b_summ_b12_20m",
        )
        fall_tcap = TasselCap(
            blue="c_fall_b02_10m",
            green="c_fall_b03_10m",
            red="c_fall_b04_10m",
            nir="c_fall_b08_10m",
            swir1="c_fall_b11_20m",
            swir2="c_fall_b12_20m",
        )

        self.collection = (
            self.collection.addCalculator(spri_tcap)
            .addCalculator(summ_tcap)
            .addCalculator(fall_tcap)
        )
        return self

    def build(self):
        """builds the data cube collection"""
        self.collection = self.collection.select("a_spri_b.*|b_summ_b.*|c_fall_b.*")
        return self


class Sentinel1Builder:
    def __init__(self) -> None:
        self.collection = None

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        self.collection = value

    def addSpatialFilter(self, geometry: ee.Geometry) -> None:
        """adds a spatial filter to the input collection"""
        self.collection = self.collection.filterBounds(geometry)
        return self

    def addBoxCar(self):
        """adds a boxcar filter to the collection"""
        boxcar = BoxCar(1)
        self.collection = self.collection.denoise(boxcar)
        return self

    def addRatio(self):
        """adds a ratio to the collection"""
        ratio = Ratio("VV", "VH")
        self.collection = self.collection.addCalculator(ratio)
        return self

    def build(self) -> ee.ImageCollection:
        """builds the Sentinel1 collection"""
        self.collection = self.collection.select("V.*")
        return self


class ALOSBuilder:
    def __init__(self) -> None:
        self.collection = ee.ImageCollection(ImageCollectionIDs.alos)

    def addTemportalFilter(self, start: str, end: str):
        self.collection = self.collection.filterDate(start, end)
        return self

    def addBoxCar(self):
        """adds a boxcar filter to the collection"""
        boxcar = BoxCar(1)
        self.collection = self.collection.denoise(boxcar)
        return self

    def addRatio(self):
        """adds a ratio to the collection"""
        ratio = Ratio("HH", "HV")
        ratio.name = "HH/HV"
        self.collection = self.collection.addCalculator(ratio)
        return self

    def build(self):
        self.collection = self.collection.select("H.*").first()
        return self


class FourierBuilder:
    def __init__(self) -> None:
        self.collection = None

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        if not isinstance(value, ee.ImageCollection):
            raise TypeError("Input must be an ee.ImageCollection")
        self._collection = value

    def addSpatialFilter(self, geometry: ee.Geometry) -> None:
        """adds a spatial filter to the input collection"""
        self.collection = self.collection.filterBounds(geometry)
        return self

    def build(self):
        return self


class TerrainBuilder:
    def __init__(self) -> None:
        self.collection = None

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        if not isinstance(value, ee.ImageCollection):
            raise TypeError("Input must be an ee.ImageCollection")
        self._collection = value

    def addSpatialFilter(self, geometry: ee.Geometry) -> None:
        """adds a spatial filter to the input collection"""
        self.collection = self.collection.filterBounds(geometry)
        return self

    def build(self):
        return self


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


class TrainingPointBuilder:
    def __init__(self) -> None:
        self.collection = None

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        if not isinstance(value, TrainingPoints):
            raise TypeError("Input must be an TrainingPoints")
        self._collection = value

    def addXCoordinate(self):
        self.collection = self.collection.addXCoordinate()
        return self

    def addYCoordinate(self):
        self.collection = self.collection.addYCoordinate()
        return self

    def addLabelValues(self):
        self.collection = self.collection.addValues()
        return self

    def build(self):
        return self


class SampleBuilder:
    def __init__(self) -> None:
        self.collection = None

    def addStack(self, stack: ee.Image):
        ...

    def build(self):
        return self
