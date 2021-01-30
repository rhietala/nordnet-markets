from analyze import analyze, draw
from symbols import Symbol, SYMBOLS

from get_data import get_data

# Same as bot.py, but don't post anything to discord, only to terminal

get_data()

for (index, symbol) in enumerate(SYMBOLS):
    print("{0} ({1}/{2})".format(symbol.name, index + 1, len(SYMBOLS)))
    (df, highlight, explanation) = analyze(symbol)
    if highlight:
        print(explanation)
        draw(symbol, df)
