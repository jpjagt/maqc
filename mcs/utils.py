import sys
import json


def load_json(fpath):
    with open(fpath) as f:
        return json.loads(f.read())


def get_station_codes_from_columns(columns):
    return [
        col
        for col in columns
        if isinstance(col, str) and len(col) == 7 and col.startswith("NL")
    ]


def get_ts_df(df, ts_col="Begindatumtijd", resample_to=None):
    station_codes = get_station_codes_from_columns(df.columns)

    # set the ts col as the index, and get just the station measurements
    ts_df = df.set_index(ts_col)[station_codes]

    # make sure the data is chronological
    ts_df = ts_df.sort_index()

    # remove duplicate timestamps
    ts_df = ts_df[~ts_df.index.duplicated()]

    # make sure we have a row for every hour
    ts_df = ts_df.asfreq("H")

    # fill missing values using ffill
    ts_df[station_codes] = ts_df[station_codes].ffill()

    if resample_to:
        ts_df = ts_df.resample(resample_to).mean()

    return ts_df


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
