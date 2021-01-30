from datetime import date
from pandas import json_normalize as pd_json_normalize, to_datetime as pd_to_datetime  # type: ignore
from json import loads as json_loads
from requests import get
from dotenv import load_dotenv  # type: ignore
from os import getenv, path

from symbols import Symbol, SYMBOLS

# Marketstack API endpoint
MARKETSTACK_URL = "http://api.marketstack.com/v1/eod"

# Directory for saving Marketstack raw data
DATA_DIR = "./data"

# Environment variables that should be defined for these functions:
# - MARKETSTACK_API_KEY
load_dotenv()


def get_data():
    """
    Download end-of-day data from Marketstack to json files in DATA_DIR

    Loops through symbols defined in symbols.py, skips downloading those
    symbols that have already been downloaded to limit api requests.
    """
    now = date.today()

    print("Getting data from {0}".format(MARKETSTACK_URL))

    for (index, symbol) in enumerate(SYMBOLS):
        filename = "{0}/{1}-{2}.json".format(DATA_DIR, now, symbol.symbol_marketstack)
        exists = path.isfile(filename)

        exists_text = "already exists " if exists else ""
        print(
            "{0} => {1} {2}({3}/{4})".format(
                symbol.name, filename, exists_text, index + 1, len(SYMBOLS)
            )
        )

        if not exists:
            response = get(
                MARKETSTACK_URL,
                params={
                    "access_key": getenv("MARKETSTACK_API_KEY"),
                    "limit": 1000,
                    "symbols": symbol.symbol_marketstack,
                },
            )
            with open(filename, mode="w") as file:
                file.write(response.text)


def read_file(symbol: Symbol):
    """
    Read today's marketstack data file

    :param symbol: market symbol being read
    :returns: pandas dataframe indexed by date
    """
    now = date.today()
    filename = "{0}/{1}-{2}.json".format(DATA_DIR, now, symbol.symbol_marketstack)
    with open(filename, mode="r") as file:
        raw = file.read()

    df = pd_json_normalize(json_loads(raw), "data")
    df["date"] = pd_to_datetime(df["date"])
    df = df.set_index("date")
    df = df.reindex(index=df.index[::-1])
    return df
