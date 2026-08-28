from machine import ADC, Pin
import time

ao     = ADC(Pin(36))            # аналоговий вхід KY-026 (напр. GPIO36 на ESP32)
THRESH = 1200                    # поріг у сирих одиницях — підбери під свою сцену

while True:
    ir = ao.read()               # 0..4095: більше ІЧ (ближче/сильніше вогонь) — інше число
    print(ir)                    # дивись у REPL, підбери THRESH під свій вогонь
    if ir > THRESH:
        pass                     # тут — «жару достатньо»: у робота це «повертай на найяскравіше й гаси»
    time.sleep_ms(50)
