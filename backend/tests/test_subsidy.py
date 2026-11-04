import pytest

from app.logic.subsidy import calculate_subsidy


def test_one_kw():
    assert calculate_subsidy(1, 30000, 2, 18000, 78000) == 30000


def test_two_kw():
    assert calculate_subsidy(2, 30000, 2, 18000, 78000) == 60000


def test_three_kw():
    assert calculate_subsidy(3, 30000, 2, 18000, 78000) == 78000


def test_five_kw():
    assert calculate_subsidy(5, 30000, 2, 18000, 78000) == 78000


def test_invalid_kw():
    with pytest.raises(ValueError):
        calculate_subsidy(0, 30000, 2, 18000, 78000)


def test_negative_subsidy():
    with pytest.raises(ValueError):
        calculate_subsidy(2, -30000, 2, 18000, 78000)