def decide(sensor, heater, threshold):
    t = sensor.read()                # ← шов: чим є sensor — вирішують ЗЗОВНІ
    if t < threshold:
        heater.on()
    else:
        heater.off()

# точка ввімкнення — головний код обирає, ЩО під'єднати до шва:
decide(RealSensor(), RealHeater(), 20.0)      # у продакшені — справжнє залізо
decide(FakeSensor(reads=19.0), SpyHeater(), 20.0)  # у тесті — підробки
