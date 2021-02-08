from datetime import date
from matplotlib.pyplot import figure  # type: ignore
from matplotlib.gridspec import GridSpec  # type: ignore
from matplotlib.transforms import Bbox  # type: ignore
from numpy import vstack  # type: ignore
from typing import Any, Tuple
from urllib.parse import quote as quote_url

from symbols import Symbol, SYMBOLS
from get_data import read_file

# Analyze window sizes, short is for the actual analysis and
# long is for trend
WINDOW_SIZE_SHORT = 10
WINDOW_SIZE_LONG = 100

STOCHASTIC_WINDOW_SIZE_K = 5
STOCHASTIC_WINDOW_SIZE_K_SMOOTH = 3
STOCHASTIC_WINDOW_SIZE_D = 3
STOCHASTIC_UPPER_LIMIT = 0.8
STOCHASTIC_LOWER_LIMIT = 0.2

ALL_TIME_HIGH_RANGE = 0.97

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

    All-time high:
    - ath: highest value ever
    - ath_95: 95% of the highest value

    Highlighting is done if
    - last close is above bb_upper AND ema_long_delta (trend) is positive, or
    - last close is under bb_lower AND ema_long_delta (trend) is negative
    - stochastic K and D are both over 0.8
    - stochastic K and D are both under 0.2
    - last high is over 95% of all-time high

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

    # stocahstic
    df["stoch_k_highest"] = df.high.rolling(window=STOCHASTIC_WINDOW_SIZE_K).max()
    df["stoch_k_lowest"] = df.low.rolling(window=STOCHASTIC_WINDOW_SIZE_K).min()
    df["stoch_k_raw"] = (df["close"] - df["stoch_k_lowest"]) / (
        df["stoch_k_highest"] - df["stoch_k_lowest"]
    )
    df["stoch_k"] = (
        df["stoch_k_raw"].rolling(window=STOCHASTIC_WINDOW_SIZE_K_SMOOTH).mean()
    )
    df["stoch_d"] = df["stoch_k"].rolling(window=STOCHASTIC_WINDOW_SIZE_D).mean()

    # all-time high
    df["ath"] = df["high"].cummax()
    df["ath_lower"] = df["ath"] * ALL_TIME_HIGH_RANGE

    opn = df["open"].iat[-1]
    close = df["close"].iat[-1]
    high = df["high"].iat[-1]
    low = df["low"].iat[-1]
    trend = df["ema_long_delta"].iat[-1]
    bb_upper = df["bb_upper"].iat[-1]
    bb_lower = df["bb_lower"].iat[-1]
    stoch_k = df["stoch_k"].iat[-1]
    stoch_d = df["stoch_d"].iat[-1]
    ath_lower = df["ath_lower"].iat[-1]

    summary = "{0}\n".format(symbol.name)
    summary += "```\n"
    summary += "open     {0:>4.2f}\n".format(opn)
    summary += "close    {0:>4.2f}\n".format(close)
    summary += "high     {0:>4.2f}\n".format(high)
    summary += "low      {0:>4.2f}\n".format(low)
    summary += "```\n"
    summary += "<{0}?symbol={1}>".format(TRADINGVIEW_URL, symbol.symbol_tradingview)

    highlight = False

    if (close > bb_upper and trend < 0) or (
        stoch_k > 0.8 and stoch_d > 0.8 and trend > 0
    ):
        nordnet_url = "{0}?direction={1}&underlyingName={2}".format(
            NORDNET_LISTING_URL, "D", quote_url(symbol.name)
        )
        summary += "\n<{0}>".format(nordnet_url)
        highlight = True

    if (close < bb_lower and trend > 0) or (
        stoch_k < 0.2 and stoch_d < 0.2 and trend > 0 or (high > ath_lower)
    ):
        nordnet_url = "{0}?direction={1}&underlyingName={2}".format(
            NORDNET_LISTING_URL, "U", quote_url(symbol.name)
        )
        summary += "\n<{0}>".format(nordnet_url)
        highlight = True

    return (df, highlight, summary)


def draw(symbol: Symbol, df) -> str:
    """
    Draw graphs for given symbol and analyzing result

    6-month graph with
    - close price line
    - high-low price area
    - hl2 exponential moving average for WINDOW_SIZE_LONG

    6-month graph with
    - volume

    14-day graph with
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

    fig = figure(figsize=(10, 10))
    fig.suptitle("{0} ({1})".format(symbol.name, symbol.symbol_tradingview))

    # gs divides the graph to two graphs vertically
    gs = GridSpec(2, 1, figure=fig)

    # top_gs divides the top graph to four vertically
    # here the hspace=0 hides top graph's x ticks, so this implies that they have to
    # share the x axis
    top_gs = gs[0].subgridspec(4, 1, hspace=0)

    # use 3/4 of the top graph for 6 month price
    ax_6mo_price = fig.add_subplot(top_gs[:-1, :], autoscaley_on=False)
    ax_6mo_price.set_ylabel("Price")

    # use 1/4 of the top graph for 6 month volume
    ax_6mo_volume = fig.add_subplot(top_gs[-1, :], sharex=ax_6mo_price)
    ax_6mo_volume.set_ylabel("Volume")

    # bottom_gs is the whole bottom graph (this is not actually required, we could
    # use the gs[1] directly, but add it for completeness and for future use)
    bottom_gs = gs[1].subgridspec(3, 1, hspace=0)

    # use 2/3 of bottom graph for 14 day price and bollinger bands
    ax_14d_price = fig.add_subplot(bottom_gs[:-1, :], autoscaley_on=False)
    ax_14d_price.set_ylabel("Price")

    # 1/3 for stochastic
    ax_stochastic = fig.add_subplot(
        bottom_gs[-1, :], sharex=ax_14d_price, yscale="logit", ylim=(10e-3, 1 - 10e-3)
    )

    ax_6mo_price.plot_date(
        x=df_6mo.index,
        y=df_6mo["close"],
        fmt="-",
        linewidth=2,
        color="black",
        label="close",
    )
    ax_6mo_price.fill_between(
        x=df_6mo.index,
        y1=df_6mo["high"],
        y2=df_6mo["low"],
        alpha=0.2,
        linewidth=1,
        color="black",
        label="high-low",
    )
    ax_6mo_price.plot_date(
        x=df_6mo.index,
        y=df_6mo["ema_long"],
        fmt="-",
        linewidth=2,
        color="blue",
        label="EMA-{0}".format(WINDOW_SIZE_LONG),
    )

    ax_6mo_price.plot_date(
        x=df_6mo.index,
        y=df_6mo["ath"],
        fmt="-",
        linewidth=1,
        color="red",
        label="all-time high",
    )

    ax_6mo_price.plot_date(
        x=df_6mo.index, y=df_6mo["ath_lower"], fmt="--", linewidth=1, color="red"
    )

    # all-time high can be outside the viewed area
    ax_6mo_price.set_ylim(
        top=max([df_6mo["high"].max(), df_6mo["ema_long"].max()]) * 1.01,
        bottom=min([df_6mo["low"].min(), df_6mo["ema_long"].min()]) * 0.99,
    )

    ax_6mo_volume.bar(df_6mo.index, df_6mo["volume"], color="black")

    ax_14d_price.plot_date(
        x=df_14d.index,
        y=df_14d["close"],
        fmt="-",
        linewidth=2,
        color="black",
        label="close",
    )
    ax_14d_price.fill_between(
        x=df_14d.index,
        y1=df_14d["high"],
        y2=df_14d["low"],
        alpha=0.2,
        linewidth=1,
        color="black",
        label="high-low",
    )
    ax_14d_price.fill_between(
        x=df_14d.index,
        y1=df_14d["bb_upper"],
        y2=df_14d["bb_lower"],
        alpha=0.2,
        linewidth=1,
        color="green",
        label="bollinger bands (EMA-{0})".format(WINDOW_SIZE_SHORT),
    )
    ax_14d_price.plot_date(
        x=df_14d.index,
        y=df_14d["ath"],
        fmt="-",
        linewidth=1,
        color="red",
        label="all-time high",
    )

    ax_14d_price.plot_date(
        x=df_14d.index, y=df_14d["ath_lower"], fmt="--", linewidth=1, color="red"
    )

    # all-time high can be outside the viewed area
    ax_14d_price.set_ylim(
        top=max([df_14d["high"].max(), df_14d["bb_upper"].max()]) * 1.01,
        bottom=min([df_14d["low"].min(), df_14d["bb_lower"].min()]) * 0.99,
    )

    ax_stochastic.plot_date(
        x=df_14d.index,
        y=df_14d["stoch_k"],
        fmt="-",
        linewidth=1,
        color="blue",
        label="stochastic %K",
    )

    ax_stochastic.plot_date(
        x=df_14d.index,
        y=df_14d["stoch_d"],
        fmt="-",
        linewidth=1,
        color="red",
        label="stochastic %D",
    )

    ax_stochastic.fill_between(
        x=df_14d.index,
        y1=STOCHASTIC_UPPER_LIMIT,
        y2=STOCHASTIC_LOWER_LIMIT,
        alpha=0.2,
        linewidth=1,
        color="magenta",
    )

    ax_6mo_price.legend(loc=2)
    ax_14d_price.legend(loc=2)
    ax_stochastic.legend(loc=2)

    fig.tight_layout()
    fig.savefig(filename)

    return filename
