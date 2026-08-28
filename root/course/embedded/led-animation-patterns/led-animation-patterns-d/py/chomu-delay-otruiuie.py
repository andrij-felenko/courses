last_step = time.ticks_ms()
led_on = False

while True:
    now = time.ticks_ms()
    if time.ticks_diff(now, last_step) >= 500:  # настав час кроку?
        last_step = now                          # запам'ятали момент
        led_on = not led_on
        led.value(led_on)
    # ↓ цикл вільний — тут читаємо кнопки, ведемо зв'язок, рухаємо інші ефекти
