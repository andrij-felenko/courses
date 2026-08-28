V_SETPOINT = 1.05  # напруга бажаного проміжку (~30 см за таблицею)
KP         = 200.0  # коефіцієнт П-регулятора

while True:
    v     = read_sensor_volts()
    err   = v - V_SETPOINT       # v більша → ціль ближча, ніж треба
    drive = int(-KP * err)       # ближча → їхати назад
    drive = max(-255, min(255, drive))
    set_motor(drive)             # ваш драйвер мотора
    time.sleep_ms(20)
