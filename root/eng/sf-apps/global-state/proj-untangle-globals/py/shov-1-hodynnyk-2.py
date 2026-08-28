def build(clock):
    return Billing(clock=clock)          # поки що залежність рівно одна

def test_запізнілий_платіж_не_посуває_день_списання():
    svc = build(FixedClock(datetime(2026, 3, 3, 9, 0)))       # платіж на 2-й день пільги
    sub = Subscription("s-1", 100.0, paid_until=datetime(2026, 3, 1, 0, 0))
    assert svc.renew(sub).status == "ok"
    assert sub.paid_until == datetime(2026, 3, 31, 0, 0)      # + рівно 30д від СТРОКУ

def test_рівно_межа_пільгового_строку():
    svc = build(FixedClock(datetime(2026, 3, 4, 0, 0)))       # секунда в секунду
    sub = Subscription("s-1", 100.0, paid_until=datetime(2026, 3, 1, 0, 0))
    assert svc.renew(sub).status == "ok"

def test_на_секунду_пізніше_межі():
    svc = build(FixedClock(datetime(2026, 3, 4, 0, 0, 1)))
    sub = Subscription("s-1", 100.0, paid_until=datetime(2026, 3, 1, 0, 0))
    assert svc.renew(sub).status == "expired"
    assert sub.paid_until == datetime(2026, 3, 1, 0, 0)       # згасла — строк не рухаємо

def test_високосне_29_лютого():
    svc = build(FixedClock(datetime(2024, 2, 29, 12, 0)))
    sub = Subscription("s-1", 100.0, paid_until=datetime(2024, 2, 29, 0, 0))
    svc.renew(sub)
    assert sub.paid_until == datetime(2024, 3, 30, 0, 0)

def test_дванадцять_продовжень_без_дрейфу():
    sub = Subscription("s-1", 100.0, paid_until=datetime(2026, 1, 1))
    for _ in range(12):
        build(FixedClock(sub.paid_until + timedelta(days=2))).renew(sub)   # щоразу +2д
    assert sub.paid_until == datetime(2026, 1, 1) + timedelta(days=360)    # дрейф 0
