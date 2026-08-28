from machine import I2C, Pin

# Wire.begin() → створення шини; scan() сам стукає по всіх адресах 1..126
i2c = I2C(0, scl=Pin(22), sda=Pin(21))   # типові виводи ESP32

print("Скан I2C-шини...")
found = i2c.scan()                       # список адрес, що підтвердили себе
for addr in found:
    print("  знайдено пристрій за 0x{:02X}".format(addr))
if not found:
    print("  тиша. Перевір живлення, SDA/SCL і підтяжки.")
