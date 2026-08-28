gcc main.o libsensor.a -o app     # ПРАВИЛЬНО
# крок 1: лінкер бере main.o безумовно → з'являється дірка sensor_read
# крок 2: доходить до libsensor.a, бачить відкриту дірку sensor_read
#         → витягує sensor.o з архіву, дірку закрито ✓

gcc libsensor.a main.o -o app     # НЕПРАВИЛЬНО
# крок 1: лінкер дивиться libsensor.a — відкритих дірок ЩЕ нема
#         → не бере з неї нічого, минає порожньою
# крок 2: бере main.o безумовно → аж тепер з'являється дірка sensor_read
#         → але бібліотеку вже минули, брати нема звідки
#         → undefined reference to sensor_read ✗
