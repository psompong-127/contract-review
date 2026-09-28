from checkers import extract_numbers, normalize_numbers

import pytest

def test_unknown_unit_raises_clear_error():
    with pytest.raises(ValueError):
        extract_numbers("1 month", "month")


def test_digits_with_word_in_front():
    assert extract_numbers("not exceed forty (40) hours per week", "hours") == [40]


def test_bare_digits():
    assert extract_numbers("48 hours per week", "hours") == [48]


def test_spelled_out_word():
    assert extract_numbers("on one month's notice", "months") == [1]


def test_word_with_digits_in_brackets():
    assert extract_numbers("one (1) month's written notice", "months") == [1]


def test_wrong_unit_returns_empty():
    assert extract_numbers("forty (40) hours", "months") == []


def test_normalize_keeps_surrounding_text():
    assert normalize_numbers("within thirty (30) days") == "within 30 days"