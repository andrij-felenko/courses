import board, busio
from adafruit_bus_device.i2c_device import I2CDevice

FT_ADDR    = 0x38
FT_REG_NUM = 0x02   # кількість дотиків
FT_REG_P1  = 0x03   # початок блоку першої точки

i2c = busio.I2C(board.SCL, board.SDA)
dev = I2CDevice(i2c, FT_ADDR)

def ft6206_read():
    b = bytearray(7)                        # лічильник + 6 байтів точки
    with dev:
        # пишемо адресу регістра, тоді вичитуємо 0x02..0x08 поспіль
        dev.write_then_readinto(bytes([FT_REG_NUM]), b)

    touches = b[0] & 0x0F                    # молодші біти — кількість
    if touches == 0:
        return (0, 0, 0)

    # координата 12-бітна: старший байт дає лише 4 біти, верхні — службові
    x = ((b[1] & 0x0F) << 8) | b[2]         # b[1]=0x03, b[2]=0x04
    y = ((b[3] & 0x0F) << 8) | b[4]         # b[3]=0x05, b[4]=0x06
    return (x, y, touches)
