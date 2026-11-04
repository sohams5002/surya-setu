import pytest

from app.logic.sizing import calculate_solar_size


def test_85_units():
    assert calculate_solar_size(85) == 1


def test_175_units_round_half_up():
    assert calculate_solar_size(175) == 2


def test_210_units():
    assert calculate_solar_size(210) == 2


def test_340_units():
    assert calculate_solar_size(340) == 3


def test_350_units():
    assert calculate_solar_size(350) == 3


def test_zero_consumption():
    assert calculate_solar_size(0) == 1


def test_negative_consumption():
    with pytest.raises(ValueError):
        calculate_solar_size(-100)


def test_zero_generation():
    with pytest.raises(ValueError):
        calculate_solar_size(100, 0)


def test_negative_generation():
    with pytest.raises(ValueError):
        calculate_solar_size(100, -1400)


def test_nan_consumption():
    with pytest.raises(ValueError):
        calculate_solar_size(float("nan"))


def test_infinite_generation():
    with pytest.raises(ValueError):
        calculate_solar_size(100, float("inf"))