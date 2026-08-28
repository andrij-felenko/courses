import signal

def install_signal_handlers():
    """Зробити так, щоб kill (SIGTERM) виходив ТИМИ САМИМИ дверима, що й Ctrl+C,
    тобто крізь finally. Без цього SIGTERM убиває процес до прибирання."""
    def _graceful(signum, frame):
        # перетворюємо зовнішній сигнал на звичайний керований виняток
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, _graceful)
    # SIGINT (Ctrl+C) Python і так робить KeyboardInterrupt — його чіпати не треба
