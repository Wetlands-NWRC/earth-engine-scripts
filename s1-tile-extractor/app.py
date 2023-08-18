print("Starting...")
print("Loading modules...", end="\n\n")
import os
import json
import sys
import warnings

warnings.filterwarnings("ignore")  # this is for pandas


try:
    import ee
    import geopandas as gpd
    import pandas as pd
    from eeng.server.image_collection import Sentinel1Creator

    ee.Initialize()

except ImportError as e:
    print("Some modules are missing {}".format(e))


# helper to convert the image collection to a feature collection
# convert server to client object


def extract_from_ee_menu() -> None:
    CRS = "EPSG:4326"

    aoi = input("Enter the AOI (ASSET): ")
    start = input("Enter the start date (YYYY-MM-DD): ")
    end = input("Enter the end date (YYYY-MM-DD): ")
    outdir = input("Enter the output directory: ")

    # convert the aoi to a geometry
    extract_from_ee(aoi, start, end, outdir)


def extract_from_ee(aoi, start, end, outdir):
    aoi = ee.FeatureCollection(aoi).geometry().bounds()

    # get the sentinel 1 dv image collection
    s1_dv = Sentinel1Creator().get_dv_col(start_date=start, end_date=end, geometry=aoi)

    s1_dv = s1_dv.addFDate().addPrefix().addGroupId()
    s1_dv_fc = s1_dv.toFeatureCollection()

    # convert server obj to client obj
    response = s1_dv_fc.getInfo()["features"]

    # to dataframe
    gdf = gpd.GeoDataFrame.from_features(response)
    gdf2 = gdf[
        [
            "date",
            "group_id",
            "relativeOrbitNumber_start",
            "platform_number",
            "orbitProperties_pass",
            "system_id",
            "geometry",
        ]
    ]
    gdf["transmitterReceiverPolarisation"] = gdf[
        "transmitterReceiverPolarisation"
    ].apply(", ".join)
    # old: new

    new_column_names = {
        "relativeOrbitNumber_start": "relorb",
        "orbitProperties_pass": "look_dir",
    }

    gdf2.rename(columns=new_column_names, inplace=True)

    # export the table
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    full_out_name = f's1_dv_{start.replace("-", "_")}_{end.replace("-", "_")}.geojson'
    gdf.set_crs(epsg="4326").to_file(
        os.path.join(outdir, full_out_name), driver="GeoJSON"
    )

    platform_numbers = gdf["platform_number"].unique().tolist()
    gdfs = []
    for platform_number in platform_numbers:
        short_out_nmae = f's1_dv_{start.replace("-", "_")}_{end.replace("-", "_")}_{platform_number}.shp'
        gdfs.append((short_out_nmae, gdf2[gdf2["platform_number"] == platform_number]))

    for filename, gdf in gdfs:
        gdf.set_crs(epsg="4326").to_file(
            os.path.join(outdir, filename), driver="ESRI Shapefile"
        )
    # export aoi to shapefile
    fc = ee.FeatureCollection([ee.Feature(aoi, {"name": "aoi"})])
    gdf_aoi = gpd.GeoDataFrame.from_features(fc.getInfo()["features"])

    aoi_path = os.path.join(outdir, "aoi")
    if not os.path.exists(aoi_path):
        out_name = os.path.join(outdir, "aoi.shp")
        gdf_aoi.set_crs(epsg=4326, inplace=True).to_file(
            out_name, driver="ESRI Shapefile"
        )

    print("Done!")
    return None


def extract_swaths_from_file():
    from eeng.client.gdftools import extract_s1_swaths

    spatial_file = input("Enter the spatial file (Shapefile): ")
    rel_orbit_number = input("Enter the relative orbit number(s): ")
    outdir = input("Enter the output directory: ")

    trg_obrits = list(map(int, rel_orbit_number.strip().split(",")))
    gdf = gpd.read_file(spatial_file)
    swaths = extract_s1_swaths(gdf=gdf, relobits=trg_obrits)

    filename = f's1_dv_{"_".join(list(map(str, trg_obrits)))}.shp'
    swaths["date"] = pd.to_datetime(swaths["date"]).dt.strftime("%Y-%m-%d")
    swaths.to_file(os.path.join(outdir, filename))
    print("Done!!")
    return None


def create_s1_payload() -> None:
    from eeng.client.gdftools import extract_s1_swaths

    # 1. Get input from the user
    spatial_file = input("Enter the spatial file (Shapefile): ")
    outdir = input("Enter the output directory: ")
    gdf = gpd.read_file(spatial_file)
    obj = {"s1": gdf["system_id"].tolist()}

    jsonfile = os.path.join(
        outdir, f"s1-payload_{os.path.splitext(os.path.basename(spatial_file))[0]}.json"
    )
    with open(jsonfile, "w") as f:
        json.dump(obj, f, indent=4)
    print("Done!")


def exit() -> None:
    """Exits the program"""
    print("Exiting...")
    sys.exit(0)


def main():
    """
    Main function

    Used to extract Sentinel-1 data from Google Earth Engine as a table. The table represents a Sentinel 1 DV image Collection.
    This us useful for further analysis in a GIS software.

    Inputs
    ------
    aoi: ee.Geometry
        Area of interest
    start_date: str
        Start date in YYYY-MM-DD format
    end_date: str
        End date in YYYY-MM-DD format
    outdir: str
        Output directory

    Exports
    -------
    Sentinel 1 DV Image Collection as a table (Shapefile)
    Sentinel 1 DV Image Collection as a table (GeoJSON)
    Bounding box of the AOI (Shapefile)
    """
    print("Welcome to the Sentinel-1 DV Image Collection Extractor!")

    while True:
        print("Please select an option: ")
        print("1. Extract Sentinel-1 DV Image Collection")
        print("2. Extract Swaths")
        print("3. Create Payload")
        print("4: Exit")
        choice = input(">>> ")

        options = {
            "1": extract_from_ee_menu,
            "2": extract_swaths_from_file,
            "3": create_s1_payload,
            "4": exit,
        }

        func = options.get(choice, None)

        if func is None:
            print(f"Invalid option: {choice}")
            print("Enter a valid option or press 3 to exit\n\n")
            continue

        func()
