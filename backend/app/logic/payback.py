def calculate_payback(
    net_cost: float,
    yearly_generation: float,
    tariff: float
) -> float:

    # Validate net cost
    if net_cost < 0:
        raise ValueError("Net cost cannot be negative")

    # Validate yearly generation
    if yearly_generation <= 0:
        raise ValueError("Yearly generation must be positive")

    # Validate tariff
    if tariff <= 0:
        raise ValueError("Tariff must be positive")

    # Calculate annual electricity savings
    yearly_savings = yearly_generation * tariff

    # Calculate payback period
    payback_years = net_cost / yearly_savings

    return round(payback_years, 2)