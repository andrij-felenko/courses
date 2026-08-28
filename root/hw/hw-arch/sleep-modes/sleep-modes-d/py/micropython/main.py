import machine, esp32
from machine import Pin

WAKE_BUTTON = 33                 # RTC-ніжка: годиться для deep-sleep
SLEEP_PERIOD_MS = 10 * 60 * 1000 # 10 хв у мс

# Лічильник переживає deep-sleep лише в RTC-пам'яті: звичайна змінна
# після перезапуску обнулиться, бо SRAM знеструмлено.
rtc = machine.RTC()
boot_count = int.from_bytes(rtc.memory() or b"\x00", "little") + 1
rtc.memory(boot_count.to_bytes(4, "little"))
print("Пробудження №%d" % boot_count)

# Зреагувати на причину: deep-sleep щоразу стартує з чистого аркуша,
# тож причину читаємо одразу на старті.
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    if machine.wake_reason() == machine.PIN_WAKE:
        print("Розбудила кнопка: поряд людина")
        # тут: увімкнути екран, лишитися активним довше
    else:
        print("Розбудив таймер: плановий замір")
        # тут: зняти давач, відіслати число
else:
    print("Холодний старт (не з deep-sleep)")

# ... корисна робота (замір, передача) ...

# Налаштувати ОБИДВА джерела перед сном: спрацює перше з них
btn = Pin(WAKE_BUTTON, Pin.IN, Pin.PULL_UP)
esp32.wake_on_ext0(pin=btn, level=esp32.WAKEUP_ALL_LOW)  # будити низьким рівнем

print("Засинаю в deep-sleep...")
machine.deepsleep(SLEEP_PERIOD_MS)
# Рядків після цього немає сенсу писати: чіп прокинеться з початку
# скрипта, а не звідси.
