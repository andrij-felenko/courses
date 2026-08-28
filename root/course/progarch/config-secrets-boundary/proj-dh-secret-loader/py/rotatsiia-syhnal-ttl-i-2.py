cfg = Config.load(manifest, store)

_wake = threading.Event()
signal.signal(signal.SIGHUP, lambda *_: _wake.set())   # сигнал ЛИШЕ будить — не фетчить у хендлері

def _rotator(ttl: float) -> None:
    while True:
        _wake.wait(timeout=ttl)      # прокидається за SIGHUP АБО коли вийшов TTL
        _wake.clear()
        cfg.reload()

threading.Thread(target=_rotator, args=(300.0,), daemon=True).start()

# ГАРЯЧИЙ шлях: знімок беруть ОДИН раз; поле-за-полем — НЕ читають.
def handle_reading(req) -> None:
    c = cfg.snapshot()                                   # цілісний знімок
    db.connect(c["db_host"], c["db_password"].expose())  # значення — лише тут
