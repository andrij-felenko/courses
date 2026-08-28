from machine import SPI, Pin

spi = SPI(1, baudrate=1_000_000, polarity=1, phase=1)
cs = Pin(5, Pin.OUT, value=1)
drdy = Pin(4, Pin.IN)

# Налаштування: коефіцієнт передискретизації задає вихідну частоту.
# Більший OSR -> повільніше, але тихіше (більше чесних розрядів).
def adc_init():
    adc_write_reg(REG_MODE, OSR_1024)    # 1024 грубих відліки на одне слово
    adc_write_reg(REG_CHAN, CH_AIN0)     # канал вимірювання

# Читання одного готового 24-бітного слова (модулятор + децимація вже в чипі).
def adc_read():
    while drdy.value():                  # чекаємо, доки фільтр зібрав слово
        pass
    b = adc_read_bytes(REG_DATA, 3)      # три байти = 24 біти
    code = (b[0] << 16) | (b[1] << 8) | b[2]
    if code & 0x800000:                  # знаковий 24-бітний код
        code -= 0x1000000                # розширюємо знак
    return code                          # готове число, можна масштабувати в вольти
