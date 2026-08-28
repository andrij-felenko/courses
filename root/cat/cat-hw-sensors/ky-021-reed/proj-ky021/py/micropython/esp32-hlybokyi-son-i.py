import machine
import esp32
from machine import Pin

PIN_REED = 25                     # ОБОВ'ЯЗКОВО RTC-здатний GPIO!

# після deep sleep чип стартує заново — уся логіка виконується «на вході»

# чому прокинулись цього разу?
if machine.wake_reason() == machine.EXT0_WAKE:
    print("прокинувся: геркон замкнувся (магніт поряд)")
else:
    print("холодний старт / скидання")

# тут — корисне діло: надіслати тривогу по Wi-Fi, інкрементувати лічбу тощо

reed = Pin(PIN_REED, Pin.IN, Pin.PULL_UP)  # внутрішня підтяжка, щоб пін не «плавав»

# готуємось спати: будити, коли PIN_REED впаде в 0 (геркон замкнений)
esp32.wake_on_ext0(pin=reed, level=esp32.WAKEUP_ALL_LOW)  # прокинутись на LOW

print("засинаю…")
machine.deepsleep()               # ← далі виконання НЕ ЙДЕ
