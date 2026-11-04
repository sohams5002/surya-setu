

from decimal import Decimal, ROUND_HALF_UP


def calculate_solar_size(
    monthly_units: float,
    generation_per_kw: float = 1400
) -> int:
    if isinstance(monthly_units,bool):
        raise ValueError("Monthly units must be a number, not a boolean.")
    try:
        monthly_units = Decimal(str(monthly_units))
    except Exception:
        raise ValueError("Monthly units must be a number.")
    
    if not monthly_units.is_finite() or monthly_units < 0:
        raise ValueError("Monthly units must be a non-negative finite number.")

    if isinstance(generation_per_kw,bool):
        raise ValueError("Generation per kW must be a number, not a boolean.")
    
    try:
        generation_per_kw = Decimal(str(generation_per_kw))
    except Exception:
        raise ValueError("Generation per kW must be a number.")
    
    if not generation_per_kw.is_finite() or generation_per_kw <= 0:
        raise ValueError("Generation per kW must be a positive finite number.")
    
    annual_units = monthly_units * Decimal("12")

    raw_kw = annual_units / generation_per_kw
    
    rounded_kw = raw_kw.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    final_kw = max(1, int(rounded_kw))

    return final_kw
    