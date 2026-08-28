from machine import I2C, Pin
import time

SENSOR_ADDR = 0x40   # адреса давача на шині I2C
LOAD_PIN    = 5      # GPIO на затвор Q1 через Rg

i2c  = I2C(0)                        # піднімаємо I2C (SDA/SCL із підтяжками зі схеми)
load = Pin(LOAD_PIN, Pin.OUT)
load.value(0)                        # навантаження вимкнене на старті

def read_sensor():
    data = i2c.readfrom_mem(SENSOR_ADDR, 0x00, 2)  # регістр 0x00, 2 байти
    return (data[0] << 8) | data[1]  # склали 16-бітове значення

while True:
    v = read_sensor()
    # залежно від давача вмикаємо силовий вихід через Q1
    load.value(1 if v > 3000 else 0)
    time.sleep_ms(100)
