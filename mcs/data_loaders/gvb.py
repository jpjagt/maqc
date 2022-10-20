import pandas as pd

from mcs.constants import GVB_DATA_DIR
from mcs.utils import load_json


def get_days_of_week(label):
    """given an arbitrary label, get the corresponding day of the week"""
    if label == "weekdays":
        return ["monday", "tuesday", "wednesday", "thursday", "friday"]
    if label in {"saturday", "sunday"}:
        return [label]
    raise ValueError(f"unrecognized format for label {label}")


class GVBDataLoader(object):
    def load_data(self, dataset_name):
        fpath = GVB_DATA_DIR / f"{dataset_name}.json"
        data = load_json(fpath)
        return data

    def load_departures_for_week(self, dataset_name):
        schedules = self.load_data(dataset_name)["schedules"]

        weekday2departures = {}

        for schedule in schedules:
            departures = [moment["departure"] for moment in schedule["times"]]
            # filter out the 24:xx:xx (past midnight) format used by GVB
            departures = [
                departure
                for departure in departures
                if not departure.startswith("24:")
            ]
            for valid_for in schedule["validFor"]:
                days_of_week = get_days_of_week(valid_for)
                for day in days_of_week:
                    if day in weekday2departures:
                        raise ValueError(
                            "multiple schedules contain departures for the same day."
                        )
                    weekday2departures[day] = departures

        return weekday2departures

    def load_departures_in_range(self, dataset_name, start, end):
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        weekday2departures = self.load_departures_for_week(dataset_name)

        departures = []
        days = pd.date_range(start, end, freq="D")
        for day in days:
            departures_on_day = weekday2departures[day.day_name().lower()]
            for departure in departures_on_day:
                departures.append(f"{day.date()} {departure}")
        departures = pd.to_datetime(departures, format="%Y-%m-%d %H:%M:%S")
        return departures[(departures > start) & (departures < end)]
