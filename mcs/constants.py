from decouple import config
from pathlib import Path

ROOT_DIR = Path(config("ROOT_DIR"))

DATA_DIR = ROOT_DIR / "data"

ASSETS_DIR = ROOT_DIR / "mcs" / "assets"

GGD_DATA_DIR = DATA_DIR / "ggd"

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
    {
        "code": "NL49020",
        "name": "Amsterdam-Jan van Galenstraat",
    },
    {
        "code": "NL49021",
        "name": "Amsterdam-Kantershof (Zuid Oost)",
    },
    {
        "code": "NL49022",
        "name": "Amsterdam-Sportpark Ookmeer (Osdorp)",
    },
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
