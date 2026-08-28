smoothed = None                      # None = «ще не ініціалізовано»

def read_ema(adc, alpha=0.2):
    global smoothed
    raw = adc.read()                                # ESP32: 0…4095
    if smoothed is None:                            # перший відлік — беремо як є
        smoothed = raw
    else:
        smoothed = alpha * raw + (1 - alpha) * smoothed
    return int(smoothed + 0.5)                      # округлення до цілого
