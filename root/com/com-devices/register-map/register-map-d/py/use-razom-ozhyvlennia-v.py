from smbus2 import SMBus

# --- адреси з даташита MPU-6050 ---
ADDR        = 0x68   # адреса чіпа на шині I2C
REG_WHO     = 0x75   # WHO_AM_I
EXPECTED_ID = 0x68   # сталий код саме цього чіпа
REG_PWR     = 0x6B   # PWR_MGMT_1
REG_CFG     = 0x1C   # ACCEL_CONFIG (діапазон у бітах 4:3)
REG_XOUT_H  = 0x3B   # старший байт виміру осі X

bus = SMBus(1)       # шина I2C №1 (типова на Raspberry Pi)

# прочитати один байт регістра reg
def readReg(reg):
    # назвати номер регістра, повторний старт, читання — усе в одному виклику
    return bus.read_byte_data(ADDR, reg)

# записати один байт val у регістр reg
def writeReg(reg, val):
    bus.write_byte_data(ADDR, reg, val)
