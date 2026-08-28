from unittest.mock import patch

def test_характеризація_продовження_із_запізненням():
    """Пришпилює ФАКТИЧНУ поведінку — включно з багом. Це не «правильно», це «як є»."""
    billing.renewals_total = 0
    with patch("billing.datetime") as dt:            # ← шов: точка вмикання ззовні
        dt.now.return_value = datetime(2026, 3, 3, 9, 0)
        sub = Subscription("s-1", 100.0, paid_until=datetime(2026, 3, 1, 0, 0))
        r = billing.renew(sub)
        assert r.status == "ok"
        assert r.amount == 102.0
        assert sub.paid_until == datetime(2026, 4, 2, 9, 0)   # ← ФАКТ, а не бажане
        assert billing.renewals_total == 1
