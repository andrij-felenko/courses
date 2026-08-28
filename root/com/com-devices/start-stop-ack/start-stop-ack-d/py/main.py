# Оцінка тривалості читання N байтів з регістра давача по I2C.
# Послідовність: S · (адр+W) · (№рег) · Sr · (адр+R) · N байтів даних · P
def i2c_read_ticks(n_bytes):
    bytes_ = 1 + 1 + 1 + n_bytes     # адр+W, №рег, адр+R, дані
    clocks = bytes_ * 9              # 9 тактів на кожен байт (8 даних + ACK)
    clocks += 3                      # S + Sr + P ≈ по одному такту
    return clocks


# За скільки часу це пройде на стандартних 100 кГц?
#   1 такт = 1 / 100000 с = 10 мкс
def i2c_read_micros(n_bytes):
    return i2c_read_ticks(n_bytes) * 10   # мкс
