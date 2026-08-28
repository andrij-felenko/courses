from machine import I2C, Pin
import time

# На ESP32/STM32/Pico ЗАДАЙТЕ свої ніжки, напр. sda=21, scl=22.
i2c = I2C(0, sda=Pin(21), scl=Pin(22))

print("\nСканую шину I2C...")

while True:
    found = 0

    # i2c.scan() сам перебирає валідні 7-бітні адреси й вертає тих, хто дав ACK
    for addr in i2c.scan():
        print("  знайдено пристрій за 0x{:02X}".format(addr), end="")
        # підкажемо, схоже це на дисплей чи ні:
        if 0x20 <= addr <= 0x27:
            print("  (схоже на PCF8574 — I2C-LCD)", end="")
        if 0x38 <= addr <= 0x3F:
            print("  (схоже на PCF8574A — I2C-LCD)", end="")
        print()
        found += 1

    if found == 0:
        print("  нічого. Перевір живлення, дроти SDA/SCL і підтяжки.")
    else:
        print("Разом пристроїв: {}".format(found))

    time.sleep(3)   # повторюємо кожні 3 с, щоб бачити, як щось зникає/з'являється
