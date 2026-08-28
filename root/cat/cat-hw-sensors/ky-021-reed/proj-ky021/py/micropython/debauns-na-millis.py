from machine import Pin
import time

PIN_REED    = 4
DEBOUNCE_MS = 10                  # вікно тиші після події (мс)

reed = Pin(PIN_REED, Pin.IN)

def magnet_present(pin: Pin) -> bool:
    return pin.value() == 0

revolutions  = 0
last_state   = False              # магніт був поряд минулого разу?
last_edge_ms = 0                  # коли востаннє зарахували край
last_report  = 0

while True:
    now   = time.ticks_ms()
    state = magnet_present(reed)

    # цікавить перехід «не було → з'явився» (край HIGH→LOW),
    # і лише якщо від минулого зарахованого краю минуло вікно тиші
    if state and not last_state and time.ticks_diff(now, last_edge_ms) >= DEBOUNCE_MS:
        revolutions += 1
        last_edge_ms = now
    last_state = state

    if time.ticks_diff(now, last_report) >= 1000:
        last_report = now
        print("обертів:", revolutions)
