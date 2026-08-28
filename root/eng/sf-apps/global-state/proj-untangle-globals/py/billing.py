# billing.py
import logging
from datetime import datetime, timedelta

settings = {"fee_rate": 0.02, "grace_days": 3, "period_days": 30}   # глобал 1: конфіг
renewals_total = 0                                                  # глобал 2: лічильник
log = logging.getLogger("billing")                                  # глобал 3: логер


def renew(sub):
    global renewals_total
    now = datetime.now()                                            # глобал 4: годинник
    deadline = sub.paid_until + timedelta(days=settings["grace_days"])
    if now > deadline:
        log.warning("sub %s: пільговий строк вичерпано", sub.id)
        return Renewal("expired", 0.0, sub.paid_until)
    amount = round(sub.plan_price * (1 + settings["fee_rate"]), 2)
    sub.paid_until = now + timedelta(days=settings["period_days"])
    renewals_total += 1
    log.info("sub %s: продовжено на %.2f", sub.id, amount)
    return Renewal("ok", amount, sub.paid_until)
