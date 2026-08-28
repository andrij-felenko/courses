from machine import Pin, I2C

SDA_PIN = 8
SCL_PIN = 9

# Типова адреса модуля GY-BMP280: SDO притягнутий до землі → 0x76.
# Якщо SDO на живленні (або в «рідному» виконанні Bosch) → 0x77.
BMP_ADDR = 0x76
REG_ID = 0xD0      # регістр ідентифікатора чипа
BMP280_ID = 0x58   # очікуване значення для BMP280

i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=100000)

# Прочитати один байт із регістра reg пристрою addr; None, якщо не відповів.
def read_reg(addr, reg):
    try:
        # readfrom_mem сам робить запис регістра + повторний старт + читання.
        data = i2c.readfrom_mem(addr, reg, 1)
    except OSError:
        return None       # давач не відповів на адресу
    return data[0]

chip_id = read_reg(BMP_ADDR, REG_ID)
if chip_id is None:
    print("За адресою 0x{:02X} ніхто не відповідає. "
          "Спробуй 0x77 і перевір дроти.".format(BMP_ADDR))
else:
    print("Регістр 0x{:02X} = 0x{:02X} — ".format(REG_ID, chip_id), end="")
    if chip_id == BMP280_ID:
        print("це BMP280, як і чекали.")
    elif chip_id == 0x60:
        print("це BME280 (з вологістю), не BMP280!")
    else:
        print("невідомий чип за цією адресою.")
