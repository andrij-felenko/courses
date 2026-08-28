from datetime import date

FACT_TTL_DAYS = 180        # доказ піврічної давнини — вже не факт, а спогад

def expire_stale_facts(reg, today=None):
    """Факт зі старим доказом вертається в припущення — його переперевірять."""
    today = today or date.today()
    for a in reg:
        stale = a.state is State.FACT and (today - a.checked_on).days > FACT_TTL_DAYS
        if stale:
            a.state = State.OPEN            # доказ протух → знову здогад у черзі
            a.claim += "  [факт протух — переперевір]"
    return reg
