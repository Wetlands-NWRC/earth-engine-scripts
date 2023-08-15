from dataclasses import dataclass


@dataclass
class Payload:
    s1 = [
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190601T220203_20190601T220228_027492_031A28_EB74",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190601T220228_20190601T220253_027492_031A28_1D62",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190601T220253_20190601T220318_027492_031A28_B0EC",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190601T220318_20190601T220343_027492_031A28_3A0C",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190731T220207_20190731T220232_028367_0334A1_0ECA",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190731T220232_20190731T220257_028367_0334A1_32FF",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190731T220257_20190731T220322_028367_0334A1_4F99",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190731T220322_20190731T220347_028367_0334A1_7758",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190606T221027_20190606T221052_027565_031C53_C63B",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190606T221052_20190606T221117_027565_031C53_1088",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190606T221117_20190606T221142_027565_031C53_7FD5",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190606T221142_20190606T221207_027565_031C53_E704",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190805T221031_20190805T221056_028440_0336C5_08AD",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190805T221056_20190805T221121_028440_0336C5_8F55",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190805T221121_20190805T221146_028440_0336C5_322A",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190805T221146_20190805T221211_028440_0336C5_0053",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190527T215404_20190527T215429_027419_0317D3_FF9D",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190527T215429_20190527T215454_027419_0317D3_48EB",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190527T215454_20190527T215519_027419_0317D3_1009",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190527T215519_20190527T215544_027419_0317D3_501E",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190726T215408_20190726T215433_028294_033253_09E6",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190726T215433_20190726T215458_028294_033253_92C9",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190726T215458_20190726T215523_028294_033253_8B6E",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190726T215523_20190726T215548_028294_033253_7A46",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20190605T221811_20190605T221836_016567_01F302_2750",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20190605T221836_20190605T221901_016567_01F302_AFE0",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190729T221905_20190729T221934_028338_0333B8_EEBB",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190729T221934_20190729T221959_028338_0333B8_1E30",
        "COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20190729T221959_20190729T222024_028338_0333B8_BD9F",
    ]
    s2 = "projects/fpca-336015/assets/cnwi-datasets/aoi_novascotia/datacube"
    fourier = "projects/fpca-336015/assets/NovaScotia/fourier_transform"
    terrain = "projects/fpca-336015/assets/NovaScotia/terrain_analysis"