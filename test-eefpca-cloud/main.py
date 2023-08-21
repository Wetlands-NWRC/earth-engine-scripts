import ee

try:
    ee.Initialize(project="fpca-336015")
    print("The Earth Engine package initialized successfully!")
except ee.EEException as e:
    print("The Earth Engine package failed to initialize!")
    print(e)
