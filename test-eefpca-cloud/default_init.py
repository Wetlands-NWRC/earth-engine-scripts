import ee

try:
    ee.Initialize()
    print("The Earth Engine package initialized successfully!")
except ee.EEException as e:
    print("The Earth Engine package failed to initialize!")
    print(e)
