from machine import Pin, I2C
import time

SDA_PIN = 8
SCL_PIN = 9

# Явно кажемо, які ноги — SDA і SCL, і на якій швидкості (100 кГц — стандарт).
i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=100000)
print("Сканую шину I2C...")

while True:
    # scan() сам перебирає адреси 0x08..0x77 і повертає ті, що відповіли ACK.
    devices = i2c.scan()
    if devices:
        for addr in devices:
            print("  знайдено пристрій за адресою 0x{:02X}".format(addr))
    else:
        print("  нікого. Перевір підтяжки, живлення й виводи.")
    print("---")
    time.sleep(3)
