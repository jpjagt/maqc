from decouple import config
from pathlib import Path

ROOT_DIR = Path(config("ROOT_DIR"))

DATA_DIR = ROOT_DIR / "data"

GGD_DATA_DIR = DATA_DIR / "ggd"
