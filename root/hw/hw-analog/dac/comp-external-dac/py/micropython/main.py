from machine import I2C, Pin

DAC = 0x60                        # MCP4725, A0 на землі
i2c = I2C(0, scl=Pin(22), sda=Pin(21))   # SDA=21, SCL=22 на класичному ESP32

def dac_set(v):                   # v: 0..4095 (12 біт)
    v &= 0x0FFF                   # лишаємо тільки 12 значущих біт
    i2c.writeto(DAC, bytes([v >> 8,      # верхні 4 біти (старший нібл = 0 → швидкий запис)
                            v & 0xFF]))  # молодші 8 біт

dac_set(2048)                     # ≈ половина шкали ≈ 1.65 В
