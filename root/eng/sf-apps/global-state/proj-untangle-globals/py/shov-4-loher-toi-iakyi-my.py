def test_згаслу_передплату_видно_в_лозі():
    recs = []
    class Cap(logging.Handler):
        def emit(self, record): recs.append(record.getMessage())
    h = Cap()
    billing.log.addHandler(h)          # ← точка вмикання: підміняємо ПРИЗНАЧЕННЯ, не логер
    try:
        billing.renew(sub)
        assert any("продовжено" in m for m in recs)
    finally:
        billing.log.removeHandler(h)
