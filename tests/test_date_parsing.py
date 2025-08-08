import os
import sys
from datetime import datetime, date
from types import SimpleNamespace

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from wordle_logs import parse_timestamp, WordleLog


@pytest.mark.parametrize(
    "timestamp_str, expected",
    [
        ("03/25/24 07:30 PM", datetime(2024, 3, 25, 19, 30)),
        ("03/25/2024 19:30", datetime(2024, 3, 25, 19, 30)),
        ("25/03/24 19:30", datetime(2024, 3, 25, 19, 30)),
        ("25/03/24 07:30:15 PM", datetime(2024, 3, 25, 19, 30, 15)),
        ("25/03/2024 19:30:15", datetime(2024, 3, 25, 19, 30, 15)),
        ("05/14/25 8:12\u00a0AM", datetime(2025, 5, 14, 8, 12)),
    ],
)
def test_parse_timestamp(timestamp_str, expected):
    assert parse_timestamp(timestamp_str) == expected


def test_parse_lines_supports_varied_dates():
    start = SimpleNamespace(value=date(2024, 3, 25))
    end = SimpleNamespace(value=date(2024, 3, 25))
    log = WordleLog(start, end)
    lines = [
        "25/03/24, 19:30:15 - Alice: Wordle 123 4/6",
        "",
        "⬛⬛⬛⬛🟨",
    ]
    log.parse_lines(lines)
    assert "Alice" in log.users
    game = log.users["Alice"].games[0]
    assert game.date == datetime(2024, 3, 25, 19, 30, 15)


def test_parse_lines_with_nonbreaking_space():
    start = SimpleNamespace(value=date(2025, 5, 14))
    end = SimpleNamespace(value=date(2025, 5, 14))
    log = WordleLog(start, end)
    lines = [
        "05/14/25, 8:12\u00a0AM - John Smith: Wordle 1,425 5/6",
        "",
        "⬛⬛⬛⬛🟨",
    ]
    log.parse_lines(lines)
    assert "John Smith" in log.users
    game = log.users["John Smith"].games[0]
    assert game.date == datetime(2025, 5, 14, 8, 12)
    assert game.puzzle_number == 1425
