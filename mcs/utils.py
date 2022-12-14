import os
import sys
import json
import calendar
import pandas as pd

from mcs.constants import DATE_FOR_RELATIVE_TIME_OF_DAY


def load_json(fpath):
    with open(fpath) as f:
        return json.loads(f.read())


def get_ts_dfknmi(df, ts_col="timestamp", resample_to=None):
    # set the ts col
    ts_df = df.set_index(ts_col).asfreq("30s")
    # make sure the data is chronological
    ts_df = ts_df.sort_index()
    # remove duplicate timestamps
    ts_df = ts_df[~ts_df.index.duplicated()]
    ts_df = ts_df.ffill()
    if resample_to:
        ts_df = ts_df.resample(resample_to).mean()

    return ts_df


def query_yes_no(
    question, default=None, remark_if_yes=None, remark_if_no=None
):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            outcome = valid[default]
            break
        elif choice in valid:
            outcome = valid[choice]
            break
        else:
            sys.stdout.write(
                "Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n"
            )

    if outcome is True and remark_if_yes is not None:
        print(remark_if_yes)
    if outcome is False and remark_if_no is not None:
        print(remark_if_no)

    return outcome


def set_timestamp_related_cols(df, src_col="timestamp"):
    # create date column
    df["date"] = df["timestamp"].dt.date
    # create day of week column
    cat_type = pd.CategoricalDtype(list(calendar.day_name), ordered=True)
    df["day_of_week"] = pd.Categorical.from_codes(
        df["timestamp"].dt.day_of_week, dtype=cat_type
    )
    # create normalized date column
    df["time_of_day"] = pd.to_datetime(
        DATE_FOR_RELATIVE_TIME_OF_DAY
        + " "
        + df["timestamp"].dt.time.astype(str)
    )

    df["is_weekday"] = (
        ~df["day_of_week"].str.lower().isin(["saturday", "sunday"])
    )


def rm_dir_contents(dir):
    files = dir.glob("**/*")
    for f in files:
        try:
            os.remove(f)
        except Exception:
            continue
