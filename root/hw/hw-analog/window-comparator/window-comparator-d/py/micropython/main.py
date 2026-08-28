from machine import Pin

power_ok = Pin(POWER_OK_PIN, Pin.IN)

# HIGH = живлення в нормі (обидва компаратори відпустили відкриті колектори)
if power_ok.value():                # у вікні 4.75…5.25 В
    status_led_on()                 # «живлення в нормі»
else:                               # вийшло за край вікна
    status_led_off()
    enter_safe_mode()               # напруга поза нормою — підстрахуватися
