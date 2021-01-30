from datetime import date
from matplotlib.pyplot import subplots  # type: ignore
from urllib.parse import quote as quote_url
from typing import Any, Tuple

from symbols import Symbol, SYMBOLS
from get_data import read_file

# Analyze window sizes, short is for the actual analysis and
# long is for trend
WINDOW_SIZE_SHORT = 10
WINDOW_SIZE_LONG = 100

# Directory for saving analyze graphs
GRAPH_DIR = "./graphs"

# Tradingview URL
TRADINGVIEW_URL = "https://www.tradingview.com/chart/"

# Nordnet URL for bull and bear certificates listing
NORDNET_LISTING_URL = "https://www.nordnet.fi/markkinakatsaus/sertifikaatit"


def analyze(symbol) -> Tuple[Any, bool, str]:
    """
    Analyze a company's stock data

    Fields added to dataframe:
    - hl2: high and low average
    - sma_short: hl2 simple moving average over WINDOW_SIZE_SHORT
    - sma_long: hl2 simple moving average over WINDOW_SIZE_LONG
    - ema_short: hl2 exponential moving average over WINDOW_SIZE_SHORT
    - ema_long: hl2 exponential moving average over WINDOW_SIZE_LONG
    - ema_long_delta: current and previous ema_long difference
    - stdev_short: hl2 standard deviation over WINDOW_SIZE_SHORT

    Bollinger bands:
    - bb_upper: upper bollinger band (2 * stdev_short over sma_short)
    - bb_lower: lower bollinger band (2 * stdev_short under sma_short)

    Highlighting is done if
    - last close is above bb_upper AND ema_long_delta (trend) is positive, or
    - last close is under bb_lower AND ema_long_delta (trend) is negative

    :param symbol: market symbol for analyzing
    :return (df, highlight, summary): a tuple with
     - df: pandas dataframe with added fields from analyze
     - hightlight: boolean whether this symbol should be highlighted
     - summary: summary string
    """
    df = read_file(symbol)

    df["hl2"] = (df.high + df.low) / 2
    df["sma_short"] = df.hl2.rolling(window=WINDOW_SIZE_SHORT).mean()
    df["sma_long"] = df.hl2.rolling(window=WINDOW_SIZE_LONG).mean()
    df["ema_short"] = df.hl2.ewm(span=WINDOW_SIZE_SHORT, adjust=False).mean()
    df["ema_long"] = df.hl2.ewm(span=WINDOW_SIZE_LONG, adjust=False).mean()
    df["ema_long_delta"] = df["ema_long"] - df["ema_long"].shift(1)

    df["stdev_short"] = df.hl2.rolling(window=WINDOW_SIZE_SHORT).std()

    # bollinger bands
    df["bb_upper"] = df["sma_short"] + 2 * df["stdev_short"]
    df["bb_lower"] = df["sma_short"] - 2 * df["stdev_short"]

    close = df["close"].iat[-1]
    high = df["high"].iat[-1]
    low = df["low"].iat[-1]
    trend = df["ema_long_delta"].iat[-1]
    bb_upper = df["bb_upper"].iat[-1]
    bb_lower = df["bb_lower"].iat[-1]

    summary = "Bollinger bands for {0}\n".format(symbol.name)
    summary += "```\n"
    summary += "close    {0:>4.2f}\n".format(close)
    summary += "high     {0:>4.2f}\n".format(high)
    summary += "low      {0:>4.2f}\n".format(low)
    summary += "bb upper {0:>4.2f}\n".format(bb_upper)
    summary += "bb lower {0:>4.2f}\n".format(bb_lower)
    summary += "```\n"
    summary += "<{0}?symbol={1}>".format(TRADINGVIEW_URL, symbol.symbol_tradingview)

    highlight = False

    if close > bb_upper and trend < 0:
        nordnet_url = "{0}?direction={1}&underlyingName={2}".format(
            NORDNET_LISTING_URL, "D", quote_url(symbol.name)
        )
        summary += "\n<{0}>".format(nordnet_url)
        highlight = True

    if close < bb_lower and trend > 0:
        nordnet_url = "{0}?direction={1}&underlyingName={2}".format(
            NORDNET_LISTING_URL, "U", quote_url(symbol.name)
        )
        summary += "\n<{0}>".format(nordnet_url)
        highlight = True

    return (df, highlight, summary)


def draw(symbol, df):
    """
    Draw graphs for given symbol and analyzing result

    There will be a 6-month graph with
    - close price line
    - high-low price area
    - hl2 exponential moving average for WINDOW_SIZE_LONG

    and 14-day graph with
    - close price line
    - high-low price area
    - bollinger bands area

    Graphs are stored in GRAPH_DIR

    :param symbol: market symbol for graphing
    :param df: pandas dataframe with analyze results
    """
    now = date.today()
    filename = "{0}/{1}-{2}.png".format(GRAPH_DIR, now, symbol.symbol_marketstack)

    df_6mo = df.last("6M")
    df_14d = df.last("14D")

    fig, axs = subplots(2, 1, figsize=(10, 10))

    fig.suptitle("{0} ({1})".format(symbol.name, symbol.symbol_tradingview))

    axs[0].plot_date(
        x=df_6mo.index,
        y=df_6mo["close"],
        fmt="-",
        linewidth=2,
        color="black",
        label="close",
    )
    axs[0].fill_between(
        x=df_6mo.index,
        y1=df_6mo["high"],
        y2=df_6mo["low"],
        alpha=0.2,
        linewidth=1,
        color="black",
        label="high-low",
    )
    axs[0].plot_date(
        x=df_6mo.index,
        y=df_6mo["ema_long"],
        fmt="-",
        linewidth=2,
        color="blue",
        label="EMA-{0}".format(WINDOW_SIZE_LONG),
    )

    axs[1].plot_date(
        x=df_14d.index,
        y=df_14d["close"],
        fmt="-",
        linewidth=2,
        color="black",
        label="close",
    )
    axs[1].fill_between(
        x=df_14d.index,
        y1=df_14d["high"],
        y2=df_14d["low"],
        alpha=0.2,
        linewidth=1,
        color="black",
        label="high-low",
    )
    axs[1].fill_between(
        x=df_14d.index,
        y1=df_14d["bb_upper"],
        y2=df_14d["bb_lower"],
        alpha=0.2,
        linewidth=1,
        color="green",
        label="bollinger bands (EMA-{0})".format(WINDOW_SIZE_SHORT),
    )

    axs[0].legend()
    axs[1].legend()

    fig.tight_layout()
    fig.savefig(filename)

    return filename
