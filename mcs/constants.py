from decouple import config
from pathlib import Path

ROOT_DIR = Path(config("ROOT_DIR"))

FIGURES_DIR = ROOT_DIR / "figures"

ASSETS_DIR = ROOT_DIR / "mcs" / "assets"

DATA_DIR = ROOT_DIR / "data"
GGD_DATA_DIR = DATA_DIR / "ggd"
MIT_DATA_DIR = DATA_DIR / "mit"
GVB_DATA_DIR = DATA_DIR / "gvb"
KNMI_DATA_DIR = DATA_DIR / "knmi"
UFP_DATA_DIR = DATA_DIR / "ufp"
SNIFFER_DATA_DIR = DATA_DIR / "sniffer"
DCMR_DATA_DIR = DATA_DIR / "dcmr"
CALIBRATED_DATA_DIR = DATA_DIR / "calibrated"

CAMERA_DIR = DATA_DIR / "camera"
CAMERA_IMAGES_DIR = CAMERA_DIR / "images"
IMG_LABELS_CSV_FPATH = CAMERA_DIR / "img_labels.csv"
CAMERA_LABEL_TASKS = [
    # "active_vehicles_in_front",
    # "active_vehicles_in_back",
    "nof_active_vehicles"
]

EXPERIMENT_START_DATE = "2022-11-07"
EXPERIMENT_END_DATE = "2022-11-28"
START_TIME = "06:15"
END_TIME = "16:30"

CALIBRATION_START_DATETIME = "2022-11-29 11:00:00"
CALIBRATION_END_DATETIME = "2022-12-06 11:00:00"

GGD_YEARS = list(map(str, range(2012, 2022))) + [
    "2022_01",
    "2022_02",
    "2022_03",
    "2022_04",
    "2022_05",
    "2022_06",
    "2022_07",
    "2022_08",
]

GGD_COMPONENTS = [
    "BC",
    "CO",
    "H2S",
    "NH3",
    "NO",
    "NO2",
    "NOx",
    "O3",
    "PM10",
    "PM25",
    "SO2",
]

GGD_AMSTERDAM_STATIONS = [
    {"code": "NL49003", "name": "Amsterdam-Nieuwendammerdijk"},
    {"code": "NL49007", "name": "Amsterdam-Einsteinweg"},
    {"code": "NL49012", "name": "Amsterdam-Van Diemenstraat"},
    {"code": "NL49014", "name": "Amsterdam-Vondelpark"},
    {"code": "NL49017", "name": "Amsterdam-Stadhouderskade"},
    {"code": "NL10520", "name": "Amsterdam-Florapark"},
    {"code": "NL10546", "name": "Zaanstad-Hemkade"},
    {"code": "NL49002", "name": "Amsterdam-Haarlemmerweg"},
    {"code": "NL49019", "name": "Amsterdam-Oude Schans"},
    {"code": "NL49020", "name": "Amsterdam-Jan van Galenstraat"},
    {"code": "NL49021", "name": "Amsterdam-Kantershof (Zuid Oost)"},
    {"code": "NL49022", "name": "Amsterdam-Sportpark Ookmeer (Osdorp)"},
    {"code": "NL49546", "name": "Zaanstad-Hemkade"},
    {"code": "NL49703", "name": "Amsterdam-Spaarnwoude"},
    {"code": "NL49704", "name": "Amsterdam-Hoogtij"},
    {"code": "NL10545", "name": "Amsterdam-A10 west"},
    {"code": "NL49016", "name": "Amsterdam-Westerpark"},
]

GGD_AMSTERDAM_STATION_CODES = set(
    station["code"] for station in GGD_AMSTERDAM_STATIONS
)
GGD_AMSTERDAM_STATION_NAMES = set(
    station["name"] for station in GGD_AMSTERDAM_STATIONS
)

MIT_CSV_HEADERS = [
    "is_summary",
    "deviceID",
    "timestamp",
    "latitude",
    "longitude",
    "PM1",
    "PM25",
    "PM10",
    "bin0",
    "bin1",
    "bin2",
    "bin3",
    "bin4",
    "bin5",
    "bin6",
    "bin7",
    "bin8",
    "bin9",
    "bin10",
    "bin11",
    "bin12",
    "bin13",
    "bin14",
    "bin15",
    "bin16",
    "bin17",
    "bin18",
    "bin19",
    "bin20",
    "bin21",
    "bin22",
    "bin23",
    "flowrate",
    "countglitch",
    "laser_status",
    "temperature_opc",
    "humidity_opc",
    "data_is_valid",
    "temperature",
    "humidity",
    "ambient_IR",
    "object_IR",
    "gas_op1_w",
    "gas_op1_r",
    "gas_op2_w",
    "gas_op2_r",
    "noise",
]

MIT_NUMERIC_COLUMNS = [
    "latitude",
    "longitude",
    "PM1",
    "PM25",
    "PM10",
    "bin0",
    "bin1",
    "bin2",
    "bin3",
    "bin4",
    "bin5",
    "bin6",
    "bin7",
    "bin8",
    "bin9",
    "bin10",
    "bin11",
    "bin12",
    "bin13",
    "bin14",
    "bin15",
    "bin16",
    "bin17",
    "bin18",
    "bin19",
    "bin20",
    "bin21",
    "bin22",
    "bin23",
    "flowrate",
    "countglitch",
    "laser_status",
    "temperature_opc",
    "humidity_opc",
    "data_is_valid",
    "temperature",
    "humidity",
    "ambient_IR",
    "object_IR",
    "gas_op1_w",
    "gas_op1_r",
    "gas_op2_w",
    "gas_op2_r",
    "noise",
]

BINSIZES = [
    0.35,
    0.46,
    0.66,
    1.0,
    1.3,
    1.7,
    2.3,
    3.0,
    4.0,
    5.2,
    6.5,
    8.0,
    10.0,
    12.0,
    14.0,
    16.0,
    18.0,
    20.0,
    22.0,
    25.0,
    28.0,
    31.0,
    34.0,
    37.0,
    40.0,
]
SNIFFER_CSV_HEADERS = [
    "g",
    "lat",
    "lon",
    "no2",
    "p",
    "pm10",
    "pm1_0",
    "pm2_5",
    "rh",
    "t",
    "time",
    "v",
    "voc",
]

DATE_FOR_RELATIVE_TIME_OF_DAY = "2000-01-01"
