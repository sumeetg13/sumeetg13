#!/usr/bin/env python3
"""Rotates the 'haiku of the day' between the HAIKU markers in README.md."""
import datetime
import re
from pathlib import Path

HAIKU = [
    ("petals on the queue", "each one a message in flight", "kafka keeps them all"),
    ("cold coffee, warm build", "the penguin types beside me", "green checks bloom like spring"),
    ("a workflow branches", "like cherry limbs in the wind", "every path versioned"),
    ("null pointer at dawn", "the stack trace falls like petals", "one by one, I read"),
    ("options price the storm", "volatility in full bloom", "hedge before it falls"),
    ("deploy on friday?", "the blossoms whisper: live bold", "the logs whisper: no"),
    ("one small commit lands", "ripples down the pipeline", "spring arrives in green"),
    ("the cache remembers", "what the database forgot", "both are lying, softly"),
    ("markov chains wander", "sampling the garden at night", "converging by dawn"),
    ("validation fails", "the input was a petal", "not a string at all"),
    ("branches merge at last", "conflicts settle like soft rain", "main is calm again"),
    ("a voice agent calls", "asks how your day went, then listens", "the form fills itself"),
    ("refactor at dusk", "old code falls away like bloom", "new leaves, same strong roots"),
    ("one tick, then the next", "the market breathes in candles", "patience is alpha"),
]

START, END = "<!-- HAIKU:START -->", "<!-- HAIKU:END -->"


def render(today: datetime.date) -> str:
    a, b, c = HAIKU[today.toordinal() % len(HAIKU)]
    return (f"{START}\n<p align=\"center\"><small>今日の<ruby>俳句<rt>haiku</rt></ruby> · haiku of the day</small><br/>\n"
            f"<i>{a}<br/>{b}<br/>{c}</i></p>\n{END}")


def main() -> None:
    readme = Path(__file__).resolve().parent.parent / "README.md"
    text = readme.read_text()
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), render(datetime.date.today()), text, flags=re.S)
    if new != text:
        readme.write_text(new)


if __name__ == "__main__":
    main()
