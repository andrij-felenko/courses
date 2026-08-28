THR_MAX    = 3200     # поріг одразу після бланка (гучне близьке)
THR_MIN    = 280      # поріг наприкінці вікна (кволе далеке)
TIMEOUT_US = 20000    # макс. час польоту (20 мс ≈ 3.4 м стелі)

# Спадний поріг STC у момент t (мкс від пуску): лінійно THR_MAX → THR_MIN.
def stc_threshold(t):
    if t >= TIMEOUT_US:
        return THR_MIN
    # лінійна інтерполяція
    span = THR_MAX - THR_MIN
    return THR_MIN + span * (TIMEOUT_US - t) // TIMEOUT_US
