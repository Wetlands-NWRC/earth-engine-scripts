import os
import ee
import re
import eeng
import geopandas as gpd
import pandas as pd
import time

from datetime import datetime
from typing import List

# Custom Earth Engine Modules (not available to the public)
from eeng.server.models import RandomForestModel
from eeng.server.stats import *

from stack import stack
from payload import Payload

AOIName = str


def get_file_paths(data_dir: str) -> List[str]:
    """Returns a list of file paths for the training and validation data"""
    file_paths = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".shp"):
                file_paths.append(os.path.join(root, file))
    chunk_size = 3
    files = [
        file_paths[i : i + chunk_size] for i in range(0, len(file_paths), chunk_size)
    ]
    return files


def training_gdf(trainig_file, validation_file):
    training = gpd.read_file(trainig_file)
    validation = gpd.read_file(validation_file)

    training["isTraining"] = 1
    validation["isTraining"] = 0

    gdf = pd.concat([training, validation])

    gdf.to_crs(epsg=4326, inplace=True)

    return gdf


def gdf_2_fc(gdf):
    return ee.FeatureCollection(gdf.__geo_interface__)


def table_from_lists(keys: ee.List, values: ee.List) -> ee.FeatureCollection:
    def wrapper(element: ee.ComputedObject) -> ee.Feature:
        as_list = ee.List(element)
        return ee.Feature(None, {"class_name": as_list.get(0), "value": as_list.get(1)})

    zipped = keys.zip(values)
    features = zipped.map(wrapper)
    return ee.FeatureCollection(features)


def make_assessment_table(
    matrix: ee.ComputedObject, labels: List[str] | ee.List
) -> ee.FeatureCollection:
    cfm = ee.Feature(None, {"cfm": matrix.array().slice(0, 1).slice(1, 1)})
    acc = ee.Feature(None, {"acc": matrix.accuracy()})
    pro = ee.Feature(
        None, {"pro": matrix.producersAccuracy().toList().flatten().slice(1)}
    )
    con = ee.Feature(
        None, {"con": matrix.consumersAccuracy().toList().flatten().slice(1)}
    )
    labels = ee.Feature(None, {"labels": labels})
    return ee.FeatureCollection([cfm, acc, pro, con, labels])


def main(name: AOIName):
    print("Starting Random Forest Classification Batch Process ...")
    session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Session Time: {session_time}")
    files = get_file_paths("./data")
    if len(files) == 0:
        raise Exception("No files found in ./data")
    else:
        print(f"Found {len(files)} files to process")

    for file in files:
        region, training, validation = file
        region_id = re.findall(r"\b\d{3}\b", region)[0]

        # echo to console
        print(f"Classifying {region_id}")
        print(f"Region: {region}")
        print(f"Training: {training}")
        print(f"Validation: {validation}")

        # load aoi
        aoi = gpd.read_file(region)
        aoi.to_crs(epsg=4326, inplace=True)

        print("Running on Earth Engine ...")
        # Tables
        print("Generating Tables ...")
        training = training_gdf(training, validation)
        training = gdf_2_fc(training)
        aoi = gdf_2_fc(aoi)

        print("Generating Images ...")
        img = stack(
            aoi=aoi,
            s1=Payload.s1,
            s2=Payload.s2,
            fourier=Payload.fourier,
            terrain=Payload.terrain,
        )
        print("Generating Training Data ...")
        # Set up Tranining
        training = training.addXCoordinate().addYCoordinate()
        lookupin = training.aggregate_array("class_name").distinct()
        lookupout = ee.List.sequence(1, lookupin.size())
        training = training.remap(lookupin, lookupout, "class_name")
        lookup_table = table_from_lists(lookupin, lookupout)
        print("Generating Samples ...")
        # Generate Samples
        samples = img.sampleRegions(
            collection=training,
            properties=["class_name", "isTraining", "x", "y"],
            scale=10,
            tileScale=16,
        )

        print("Generating Model ...")
        training_samples = samples.filter(ee.Filter.eq("isTraining", 1))
        validation_samples = samples.filter(ee.Filter.eq("isTraining", 0))

        # model
        model = RandomForestModel()
        model.fit(training_samples, "class_name", img.bandNames())
        print("Classifying ...")
        clfd = model.apply(img)
        print("Generating Assessment Metrics ...")
        # assessment table
        v_clfd = validation_samples.classify(model.model)
        matrix = v_clfd.errorMatrix("class_name", "classification")

        assessment_table = make_assessment_table(matrix, lookupin)
        print("Creating Tasks ...")
        # export
        root = f"{name}/output/{session_time}/{region_id}"

        # Classification Export
        file_prfix = f"{root}/classification/classified-{region_id}-"
        job_1 = ee.batch.Export.image.toCloudStorage(
            image=clfd.clip(aoi),
            description="",
            bucket="cnwi-exports",
            fileNamePrefix=file_prfix,
            region=aoi.geometry(),
            scale=10,
            fileFormat="GeoTIFF",
            maxPixels=1e13,
            fileDimensions=[2048, 2048],
            crs="EPSG:4326",
            skipEmptyTiles=True,
        )

        # Export Samples
        job_2 = ee.batch.Export.table.toCloudStorage(
            collection=samples,
            description="",
            bucket="cnwi-exports",
            fileNamePrefix=f"{root}/samples/samples-{region_id}",
            fileFormat="CSV",
        )
        # Export Lookup Table
        job_3 = ee.batch.Export.table.toCloudStorage(
            collection=lookup_table,
            description="",
            bucket="cnwi-exports",
            fileNamePrefix=f"{root}/lookup/lookup-{region_id}",
            fileFormat="CSV",
        )
        # Export Assessment Table
        job_4 = ee.batch.Export.table.toCloudStorage(
            collection=assessment_table,
            description="",
            bucket="cnwi-exports",
            fileNamePrefix=f"{root}/assessment/assessment-{region_id}",
            fileFormat="GeoJSON",
        )

        print("Starting Jobs ...")
        # start jobs
        job_1.start()
        job_2.start()
        job_3.start()
        job_4.start()
        print("Region Classification Complete ...")
        time.sleep(3)
        print("#" * 100, end="\n\n")

    print("Batch Process Complete ...")
    print("For More Information, Visit https://code.earthengine.google.com/tasks")
    print("Exiting ...")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    ee.Initialize(project="fpca-336015")
    main(name="aoi_novascotia")
