from machine import Pin
import time

RAIN = Pin(2, Pin.IN)

time.sleep_ms(50)
dry_level = RAIN.value()            # ПРИПУСКАЄМО: на старті пластина суха
print("рівень 'сухо' на цій платі =", "HIGH" if dry_level else "LOW")

while True:
    now_wet = (RAIN.value() != dry_level)   # мокро = НЕ як у спокої
    # ... далі звична логіка гістерезису/відсіву на булевому now_wet ...
