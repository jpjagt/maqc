import json
import pandas as pd
import requests
import fire
from collections import defaultdict
from datetime import datetime, timedelta
from urllib.parse import urlencode

from mcs.constants import GGD_AMSTERDAM_STATION_CODES, GGD_DATA_DIR

COLUMNS = [
    "Component",
    "Bep.periode",
    "Eenheid",
    "Begindatumtijd",
    "Einddatumtijd",
    "NL01485",
    "NL01487",
    "NL01488",
    "NL01489",
    "NL01491",
    "NL01493",
    "NL01494",
    "NL01495",
    "NL01496",
    "NL01912",
    "NL01913",
    "NL10131",
    "NL10136",
    "NL10138",
    "NL10230",
    "NL10240",
    "NL10241",
    "NL10247",
    "NL10404",
    "NL10418",
    "NL10444",
    "NL10448",
    "NL10449",
    "NL10538",
    "NL10636",
    "NL10641",
    "NL10643",
    "NL10644",
    "NL10738",
    "NL10741",
    "NL10742",
    "NL10821",
    "NL10934",
    "NL10937",
    "NL10938",
    "NL49007",
    "NL49012",
    "NL49014",
    "NL49016",
    "NL49017",
    "NL49551",
    "NL49553",
    "NL49556",
    "NL49557",
    "NL49561",
    "NL49570",
    "NL49572",
    "NL49573",
    "NL49701",
    "NL49703",
    "NL49704",
    "NL50003",
    "NL50004",
    "NL50006",
    "NL50007",
    "NL50009",
    "NL53001",
    "NL53004",
    "",
    "",
]

COMPONENT_NAME2COMPONENT_ID = {
    "NO2": "88afd3d1-6da3-496a-ac81-669a47256d34",
    "PM25": "311aa322-65bf-4f53-9341-702376f437e0",
}

PROVINCE_ID = "4a8fec5e-c1d3-49f3-84a3-28be30ae005e"

MEASUREMENTS_URL = "https://api2020.luchtmeetnet.nl/measurements"


def prepend_newlines(fpath, nlines):
    s = "fake empty line\n" * nlines
    with open(fpath, "r+") as file:
        content = file.read()
        file.seek(0)
        file.write(s + content)


def get_result_df(url):
    response = requests.get(url)
    body = json.loads(response.content)
    if "result" not in body:
        breakpoint()
    return pd.DataFrame(body["result"])


def get_stations_df():
    url = f"https://api2020.luchtmeetnet.nl/stations?show_website=true&limit=999&province_id={PROVINCE_ID}&measurement_method=active"
    return get_result_df(url)


def get_measurements_url(
    component_id, start_datetime, end_datetime, station_id
):
    return (
        MEASUREMENTS_URL
        + "/?"
        + urlencode(
            {
                "component_id": component_id,
                "start": (
                    start_datetime.astimezone()
                    .replace(microsecond=0)
                    .isoformat()
                ),
                "end": (
                    end_datetime.astimezone()
                    .replace(microsecond=0)
                    .isoformat()
                ),
                "station_id": station_id,
                "limit": 99999,
                "zero_fill": 1,
                "order_direction": "asc",
                "status": "validated,unvalidated",
            }
        )
    )


def yield_daterange_chunks(start, end, nchunks=6):
    bins = (
        pd.date_range(start=start, end=end, periods=nchunks)
        .to_series()
        .dt.round("s")
    )
    for i in range(nchunks - 1):
        yield bins[i], bins[i + 1]


def fetch_luchtmeetnet_data(year_month="2022_11"):
    year, month = map(int, year_month.split("_"))
    start_datetime = datetime(year, month, 1)
    end_datetime = datetime(year, month + 1, 1) + timedelta(seconds=-1)

    stations_df = get_stations_df()
    station_code2id = stations_df.set_index("number")["id"].loc[
        set(GGD_AMSTERDAM_STATION_CODES) & set(stations_df.number.unique())
    ]

    component_name2station_code2df = defaultdict(dict)

    for component_name, component_id in COMPONENT_NAME2COMPONENT_ID.items():
        for station_code, station_id in station_code2id.items():
            dfs = []
            for start, end in yield_daterange_chunks(
                start_datetime, end_datetime, nchunks=6
            ):
                url = get_measurements_url(
                    component_id,
                    start.to_pydatetime(),
                    end.to_pydatetime(),
                    station_id,
                )
                df = get_result_df(url)
                if df.empty:
                    continue
                if "datetime_from" not in df:
                    breakpoint()
                df["datetime_from"] = pd.to_datetime(df["datetime_from"])
                df = df.set_index("datetime_from")[["value"]]
                dfs.append(df)
            if len(dfs) > 0:
                df = pd.concat(dfs)
                df = df[~df.index.duplicated(keep="first")]
                component_name2station_code2df[component_name][
                    station_code
                ] = df

    df = pd.concat(
        {
            component_name: pd.concat(station_code2df)
            for component_name, station_code2df in component_name2station_code2df.items()
        }
    )
    df.index.names = ["component_name", "station_code", "timestamp"]
    df = df.reset_index()
    # ggd csvs are always in UTC+1 / GMT+1
    df["timestamp"] = df["timestamp"].dt.tz_convert(None) + pd.DateOffset(
        hours=1
    )
    df = df[~df.timestamp.isna()]
    component_name2df = df.pivot(
        index=["component_name", "timestamp"],
        columns="station_code",
        values="value",
    )
    for component_name in COMPONENT_NAME2COMPONENT_ID.keys():
        df = (
            component_name2df.loc[component_name]
            .reset_index()
            .rename(columns={"timestamp": "Begindatumtijd"})
        )

        # set the timestamp columns
        df["Einddatumtijd"] = (
            df["Begindatumtijd"] + pd.DateOffset(hours=1)
        ).dt.strftime("%Y%m%d %H:%M")
        df["Begindatumtijd"] = df["Begindatumtijd"].dt.strftime("%Y%m%d %H:%M")

        df["Component"] = component_name

        # ensure all columns are present
        df[list(set(COLUMNS) - set(df.columns))] = None

        out_fpath = (
            GGD_DATA_DIR / year_month / f"{year_month}_{component_name}.csv"
        )
        out_fpath.parent.mkdir(exist_ok=True, parents=True)
        # write to the file
        df[COLUMNS].to_csv(out_fpath, index=False, sep=";")
        # also, we need extra newlines to match luchtmeetnet format
        prepend_newlines(out_fpath, 7)


if __name__ == "__main__":
    fire.Fire(fetch_luchtmeetnet_data)
