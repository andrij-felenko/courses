from machine import I2C, Pin

PCF_ADDR = 0x20                 # A0..A2 = 0
i2c = I2C(0)                    # SDA/SCL за замовчуванням платформи
int_pin = Pin(4, Pin.IN, Pin.PULL_UP)   # INT відкритий стік → підтяжка вгору

# Тіньова копія порту: біти входів (P4) тримаємо в 1, решта — стани виходів.
# 0 у біті виходу = світлодіод горить (активний низький рівень).
shadow = 0xFF                   # старт: усе вимкнено, входи відпущені

def pcf_write(value):
    i2c.writeto(PCF_ADDR, bytes([value]))   # один байт — нові стани всіх 8 ніжок

def pcf_read():
    return i2c.readfrom(PCF_ADDR, 1)[0]     # знімок усіх 8 ніжок «як є»

def button_pressed(port):
    return (port & (1 << 4)) == 0   # кнопка на землю → натиснута = 0

shadow &= ~(1 << 0)             # P0 = 0 → перший світлодіод горить
shadow |=  (1 << 4)            # P4 = 1 → дозволяємо читати кнопку
pcf_write(shadow)              # одна транзакція ≈ 180 мкс на 100 кГц

while True:
    # INT в open-drain просідає в 0, коли на вході щось змінилося.
    if int_pin.value() == 0:
        port = pcf_read()               # саме читання знімає сигнал INT чипа
        if button_pressed(port):
            shadow ^= (1 << 1)          # натиск → перемкнути другий світлодіод
        pcf_write(shadow)
