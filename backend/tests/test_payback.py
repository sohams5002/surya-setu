import pytest

from app.logic.payback import calculate_payback


def test_normal_payback():
    assert calculate_payback(150000, 4200, 8) == 4.46


def test_zero_net_cost():
    assert calculate_payback(0, 4200, 8) == 0


def test_negative_cost():
    with pytest.raises(ValueError):
        calculate_payback(-1000, 4200, 8)


def test_zero_generation():
    with pytest.raises(ValueError):
        calculate_payback(100000, 0, 8)


def test_zero_tariff():
    with pytest.raises(ValueError):
        calculate_payback(100000, 4200, 0)