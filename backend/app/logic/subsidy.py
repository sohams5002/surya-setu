def calculate_subsidy(
    kw: int,
    per_kw_first:float,
    first_kw_count: int, 
    extra_kw_amount: float,
    cap: float
)-> float:
    if isinstance(kw,bool) or not isinstance(kw,int) or kw < 1:
        raise ValueError("System size must be a positive integer")

    if first_kw_count < 0:
        raise ValueError("First kW count must be a positive integer")
    
    if per_kw_first < 0 or extra_kw_amount < 0 or cap < 0:
        raise ValueError("Subsidy amounts and cap must be non-negative numbers")
    
    first_part_kw=min(kw, first_kw_count)

    first_subsidy=first_part_kw*per_kw_first

    additional_kw=max(0, kw-first_kw_count)

    additional_subsidy=additional_kw*extra_kw_amount

    total_subsidy=first_subsidy+additional_subsidy

    final_subsidy=min(total_subsidy, cap)

    return float(final_subsidy)