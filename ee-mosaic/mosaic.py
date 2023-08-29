import ee


def mosaic(elements: list[str]) -> ee.Image:
    """Mosaics an Image Collection together user ee.ImageCollection.mosaic()."""
    return ee.ImageCollection(elements).mosaic()


def main():
    to_mosaic = [
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190601T220253_20190601T220318_027492_031A28_B0EC",  # rel orb 120
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190731T220257_20190731T220322_028367_0334A1_4F99",  # rel orb 120
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190606T221052_20190606T221117_027565_031C53_1088",  # rel orb 18
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190805T221056_20190805T221121_028440_0336C5_8F55",  # rel orb 18
    ]
    img = mosaic(to_mosaic)

    assert type(img) == ee.Image

    task = ee.batch.Export.image.toDrive(
        image=img,
        description="mosaic",
        folder="s1-mosaic",
        shardSize=256,
        fileDimensions=[2048, 2048],
        crs="EPSG:4326",
    )

    # task.start()


if __name__ == "__main__":
    ee.Initialize()
    main()
