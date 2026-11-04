import pytest

from app.logic.scoring import calculate_lead_score


def test_high_score_owner():
    result = calculate_lead_score("owner", 2500)

    assert result["score"] == "High"
    assert result["next_step"] == "survey_visit"


def test_tenant_low_score():
    result = calculate_lead_score("tenant", 2500)

    assert result["score"] == "Low"
    assert result["score_reason"] == "tenant"
    assert result["next_step"] == "short_call"


def test_small_bill_low_score():
    result = calculate_lead_score("owner", 650)

    assert result["score"] == "Low"
    assert result["score_reason"] == "small bill"


def test_exact_threshold_high_score():
    result = calculate_lead_score("owner", 1000)

    assert result["score"] == "High"


def test_invalid_ownership():
    with pytest.raises(ValueError):
        calculate_lead_score("unknown", 2000)


def test_negative_bill():
    with pytest.raises(ValueError):
        calculate_lead_score("owner", -500)