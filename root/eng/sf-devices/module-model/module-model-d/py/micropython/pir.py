# pir.py — той самий взірець, інші деталі всередині
_PIR_PIN = 5
_ACTIVE_LEVEL = 1     # PIR active-high: 1 = рух

_pin = Pin(_PIR_PIN, Pin.IN)   # без підтяжки: жене сам

def pir_init():
    pass

def pir_motion():
    return _pin.value() == _ACTIVE_LEVEL
