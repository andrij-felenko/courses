t = 20.0
while True:
    try:
        t = read_sensor()     # інколи кидає
    except Exception:
        pass                  # ← помилку проковтнули, лишили старе t
    if t < THRESHOLD:         # рішення — на застарілому числі
        heater_on()
    else:
        heater_off()
    sleep(30)
