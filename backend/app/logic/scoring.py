def calculate_lead_score(
    owner_or_tenant: str,
    monthly_bill: float,
    bill_threshold: float = 1000
) -> dict:

    
    ownership = owner_or_tenant.strip().lower()

    
    if ownership not in ("owner", "tenant"):
        raise ValueError("Ownership must be owner or tenant")

  
    if monthly_bill < 0:
        raise ValueError("Monthly bill cannot be negative")

    
    if bill_threshold < 0:
        raise ValueError("Bill threshold cannot be negative")

    if ownership == "tenant":
        score = "Low"
        reason = "tenant"

    
    elif monthly_bill < bill_threshold:
        score = "Low"
        reason = "small bill"

    else:
        score = "High"
        reason = "eligible bill"


    if score == "Low":
        next_step = "short_call"
    else:
        next_step = "survey_visit"

    return {
        "score": score,
        "score_reason": reason,
        "next_step": next_step
    }