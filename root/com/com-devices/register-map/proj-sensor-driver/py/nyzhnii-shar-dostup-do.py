from smbus2 import SMBus, i2c_msg

MPU_ADDR   = 0x68
REG_WHO    = 0x75
REG_PWR    = 0x6B
REG_CFG    = 0x1C
REG_XOUT_H = 0x3B

bus = SMBus(1)   # шина I2C №1 (типова на Raspberry Pi)

# записати один байт val у регістр reg; збій шини підніме OSError
def mpu_write(reg, val):
    bus.write_byte_data(MPU_ADDR, reg, val)   # адреса регістра + дані одним обміном

# прочитати n байтів поспіль від reg; збій шини підніме OSError
def mpu_read(reg, n):
    # запис номера регістра + повторний старт + читання одним викликом ядра
    write = i2c_msg.write(MPU_ADDR, [reg])
    read  = i2c_msg.read(MPU_ADDR, n)
    bus.i2c_rdwr(write, read)                 # повторний старт між write і read
    return list(read)                          # рівно n байтів або OSError
