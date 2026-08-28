# blink.py — блимаємо світлодіодом на GPIO17, виведеному платою на макетку
# постав:  sudo apt install python3-libgpiod   (офіційна прив'язка gpiod v2)
import time
import gpiod
from gpiod.line import Direction, Value

CHIP_PATH = "/dev/gpiochip0"   # гребінка Pi у свіжому ядрі
LED_LINE  = 17                 # BCM-ім'я, надруковане на платі біля штиря

# request_lines збирає ті самі три конфіги, що в C, в один виклик:
# напрямок — вихід, початковий рівень — низький (світлодіод згаслий);
# consumer — підпис, щоб gpioinfo показував, хто зайняв лінію.
with gpiod.request_lines(
    CHIP_PATH,
    consumer="blink",
    config={
        LED_LINE: gpiod.LineSettings(
            direction=Direction.OUTPUT,
            output_value=Value.INACTIVE,
        )
    },
) as req:
    for _ in range(20):
        req.set_value(LED_LINE, Value.ACTIVE)     # горить 0.5 с
        time.sleep(0.5)
        req.set_value(LED_LINE, Value.INACTIVE)   # згас 0.5 с
        time.sleep(0.5)
# вихід із with сам звільняє лінію — окремий release не потрібен
