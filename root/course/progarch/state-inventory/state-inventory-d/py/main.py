THRESHOLD  = 20.0
MAX_RUN_S  = 2 * 3600          # безпека: не гріти довше 2 год поспіль

heater_on_flag = False         # ← стан у пам'яті процесу
on_since       = None          # ← і час теж лише в пам'яті

while True:
    t = read_sensor()
    want_on = t < THRESHOLD

    if want_on and not heater_on_flag:
        relay_on();  heater_on_flag = True;  on_since = now()
    elif not want_on and heater_on_flag:
        relay_off(); heater_on_flag = False; on_since = None

    # захисна межа рахує час від змінної в пам'яті:
    if heater_on_flag and now() - on_since > MAX_RUN_S:
        relay_off(); heater_on_flag = False; on_since = None

    report_to_cloud(heater_on_flag)   # застосунок показує цей самий прапорець
    sleep(30)
