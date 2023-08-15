from eeng.server.calc import *
from eeng.server.filters import BoxCar
from eeng.server.collections import ImageCollectionIDs


def stack(aoi, s1, s2, fourier, terrain):
    # Sentinel - 1
    spring = (135, 181)
    summer = (182, 244)
    bxcr = BoxCar(1)
    ratio = Ratio()
    s1_col = (
        ee.ImageCollection(s1)
        .filterBounds(aoi)
        .denoise(bxcr)
        .addCalculator(ratio)
        .select("V.*")
    )

    s1_spri = s1_col.filter(ee.Filter.dayOfYear(spring[0], spring[1])).mosaic()
    s1_summ = s1_col.filter(ee.Filter.dayOfYear(summer[0], summer[1])).mosaic()

    s1_img = ee.Image.cat(s1_spri, s1_summ)

    # Sentinel - 2
    # remove all non spectral bands
    s2_col = (
        ee.ImageCollection(s2)
        .filterBounds(aoi)
        .select("a_spri_b.*|b_summ_b.*|c_fall_b.*")
    )
    # create the create the calculators
    # NDVI
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

    # SAVI
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

    # TASSLED CAP
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

    s2_img = s2_col.mosaic()

    ratio.numerator = "HH"
    ratio.demoninator = "HV"
    ratio.name = "HH/HV"
    alos_img = (
        ee.ImageCollection(ImageCollectionIDs.alos)
        .filterDate("2019", "2020")
        .map(bxcr)
        .map(ratio)
        .first()
        .select("H.*")
    )

    ter_col_img = ee.ImageCollection(terrain).filterBounds(aoi).mosaic()
    four_col_img = ee.ImageCollection(fourier).filterBounds(aoi).mosaic()

    # merge all the images
    return ee.Image.cat(s1_img, s2_img, alos_img, ter_col_img, four_col_img).clip(aoi)
