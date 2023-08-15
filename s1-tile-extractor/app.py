print("Starting...")
print("Loading modules...", end="\n\n")
import os
import json
import sys
import warnings

warnings.filterwarnings('ignore') # this is for pandas


try:
    import ee
    import geopandas as gpd
    import pandas as pd
    from eeng.server.collections import ImageCollectionCreator, ImageCollectionIDs

    ee.Initialize()

except ImportError as e:
    print("Some modules are missing {}".format(e))


# define some mappable functions
def date_fmtr(image: ee.Image):
    return image.set('date', image.date().format('YYYY-MM-dd'))

def add_system_id_prefix(image: ee.Image):
    return image.set('system_id', image.get('system:id'))

def add_group_id(image: ee.Image):
    y_cent = ee.Number(image.geometry().centroid().coordinates().get(1)).format('%.2f')
    return image.set('group_id', ee.Number(image.get('relativeOrbitNumber_start')).format('%d').cat('_').cat(y_cent))


def get_s1_dv(aoi, start_date, end_date):
    s1_id = ImageCollectionIDs.s1
   
    # Create a collection of Sentinel-1 images
    s1_collection = ImageCollectionCreator(
        collection_id=s1_id,
        start=start_date,
        end=end_date,
        aoi=aoi
    )

    # Get the collection
    filter = ee.Filter([
        ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'),
        ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'),
        ee.Filter.eq('instrumentMode', 'IW'),
    ])

    return s1_collection.get_collection(filter_function=filter)


# helper to convert the image collection to a feature collection 
# convert server to client object
def convert_2_feature_collection(icollection: ee.ImageCollection) -> ee.FeatureCollection:
    """Converts a server-side object to an ee.FeatureCollection

    Args:
        icollection (ee.FeatureCollection): Server-side object to convert

    Returns:
        ee.FeatureCollection: Client-side object
    """
    as_list = icollection.toList(icollection.size())

    def computed_to_featre(element: ee.Image):
        img = ee.Image(element)
        return ee.Feature(img.geometry(), img.toDictionary())

    return ee.FeatureCollection(as_list.map(computed_to_featre))

def extract_from_ee() -> None:
    CRS = 'EPSG:4326'

    aoi = input("Enter the AOI (ASSET): ")
    start = input("Enter the start date (YYYY-MM-DD): ")
    end = input("Enter the end date (YYYY-MM-DD): ")
    outdir = input("Enter the output directory: ")

    # convert the aoi to a geometry
   
    aoi = ee.FeatureCollection(aoi).geometry().bounds()
    
    # get the sentinel 1 dv image collection
    s1_dv = get_s1_dv(aoi, start, end)

    # add some properties to the image collection
    s1_dv = s1_dv.map(date_fmtr).map(add_system_id_prefix).map(add_group_id)

    # convert the image collection to a feature collection
    s1_dv = convert_2_feature_collection(s1_dv)


    # convert server obj to client obj
    response = s1_dv.getInfo()['features']
    
    # to dataframe
    gdf = gpd.GeoDataFrame.from_features(response)
    gdf2 = gdf[['date', 'group_id', 'relativeOrbitNumber_start', 'orbitProperties_pass', 'system_id', 'geometry']]
    gdf['transmitterReceiverPolarisation'] = gdf['transmitterReceiverPolarisation'].apply(', '.join)
    # old: new
    new_column_names = {
        'relativeOrbitNumber_start': 'relorb',
        'orbitProperties_pass': 'look_dir',
    }

    gdf2.rename(columns=new_column_names, inplace=True)

    # export the table
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    full_out_name = f's1_dv_{start.replace("-", "_")}_{end.replace("-", "_")}.geojson'
    gdf.set_crs(epsg='4326').to_file(os.path.join(outdir, full_out_name), driver='GeoJSON')
    short_out_nmae = f's1_dv_{start.replace("-", "_")}_{end.replace("-", "_")}.shp'
    gdf2.set_crs(epsg='4326').to_file(os.path.join(outdir, short_out_nmae), driver='ESRI Shapefile')
    
    # export aoi to shapefile
    fc = ee.FeatureCollection([ee.Feature(aoi, {'name': 'aoi'})])
    gdf_aoi = gpd.GeoDataFrame.from_features(fc.getInfo()['features'])

    aoi_path = os.path.join(outdir, 'aoi')
    if not os.path.exists(aoi_path):
        out_name = os.path.join(outdir, 'aoi.shp')
        gdf_aoi.set_crs(epsg=4326, inplace=True).to_file(out_name, driver='ESRI Shapefile') 

    print("Done!")
    return None


def extract_by_date(gdf: gpd.GeoDataFrame):
    """ Extracts tiles that fall cloesest to the mid point of the date range
        These ranage are from the data cube composites feature class

        Early Season DOY: 135 - 181
        Mid Season DOY: 182 - 243
        Late Season DOY: 245 - 274

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame containing the tiles

    Returns:
        gpd.GeoDataFrame: GeoDataFrame containing the tiles that fall closest to the midpoint
       """
    
    def calc(gdf): return (gdf['doy'].min() + gdf['doy'].max()) // 2

    # add the doy from the date column
    gdf['date'] = pd.to_datetime(gdf['date'], format='%Y-%m-%d')
    gdf['doy'] = gdf['date'].dt.dayofyear

    swaths = []
    for rel_orbit in gdf['relorb'].unique():
        in_gdf = gdf[gdf['relorb'] == rel_orbit]
        early_season = in_gdf[(in_gdf['doy'] >= 135) & (in_gdf['doy'] <= 181)]
        mid_season = in_gdf[(in_gdf['doy'] >= 182) & (in_gdf['doy'] <= 243)]

        early_season['mid_point'] = calc(early_season)
        mid_season['mid_point'] = calc(mid_season)

        early_season['diff'] = early_season.apply(lambda x: x['doy'] - x['mid_point'], axis=1)
        mid_season['diff'] = mid_season.apply(lambda x: x['doy'] - x['mid_point'], axis=1)

        early_season['diff_abs'] = early_season['diff'].abs()
        mid_season['diff_abs'] = mid_season['diff'].abs()
        # TODO will need to add more complex logic here at some point to add a stop condition want to select images on the positive side of the mid point, if then check the negative side if there are no images on the positive side
        early_season = early_season[early_season['diff_abs'] == early_season['diff_abs'].min()]
        mid_season = mid_season[mid_season['diff_abs'] == mid_season['diff_abs'].min()]

        early_season = early_season[early_season['diff'] <= 0]
        mid_season = mid_season[mid_season['diff'] <= 0]

        swaths.extend([early_season, mid_season])
    return pd.concat(swaths)


def create_s1_payload() -> None:

    # 1. Get input from the user
    # 1.a Get the spatial file that has the tiles
    spatial_file = input("Enter the spatial file (Shapefile): ")
    # 1.b Get the relative orbit number(s) that the user wants to extract
    rel_orbit_number = input("Enter the relative orbit number(s): ")
    # 1.c Get the output directory
    outdir = input("Enter the output directory: ")
    # 2. Load the spatial file
    gdf = gpd.read_file(spatial_file)
    # 3. Slice the dataframe based on the relative orbit number(s)
    trg_obrits = list(map(int, rel_orbit_number.strip().split(',')))
    sliced_df = gdf[gdf['relorb'].isin(trg_obrits)]
    # partition the dataframe based on the relative orbit number and season
    sliced_df = extract_by_date(sliced_df)
    # 3. Once we have the sliced dataframe, we can send the tile ids to dict
    obj = {"s1": sliced_df['system_id'].tolist()}
    # 4. serialize the dict to json
    jsonfile = os.path.join(outdir, f's1-payload_{os.path.splitext(os.path.basename(spatial_file))[0]}.json')
    with open(jsonfile, 'w') as f:
        json.dump(obj, f, indent=4)
    # 5. save the sliced dataframe as a shapefile
    filename = f"s1_payload_{os.path.splitext(os.path.basename(spatial_file))[0]}.shp"
    out_spatial_file = os.path.join(outdir, filename)
    sliced_df['date'] = sliced_df['date'].astype(str)
    sliced_df.to_file(out_spatial_file, driver='ESRI Shapefile')
    print("Done!")


    # read the shapefile

    # parse the relative orbit number
    rel_orbit_number = rel_orbit_number.split(',')

    # files a shapefile 
    # and a json file
    # { 's1': [tile_id, ...] }

    tiles = []

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
        print("2. Create Sentinel-1 DV Image Collection Payload")
        print("3. Exit")
        choice = input(">>> ")
        
        options = {
            '1': extract_from_ee,
            '2': create_s1_payload,
            '3': exit
        }

        func = options.get(choice, None)

        if func is None:
            print(f"Invalid option: {choice}")
            print("Enter a valid option or press 3 to exit\n\n")
            continue

        func()
