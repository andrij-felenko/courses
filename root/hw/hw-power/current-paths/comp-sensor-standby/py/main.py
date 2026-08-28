from machine import I2C, Pin
import machine

BME280_ADDR   = 0x76  # або 0x77 (ADR=1)
LIS3DH_ADDR   = 0x18  # або 0x19 (SA0=1)
BME_CTRL_MEAS = 0xF4  # mode[1:0] → 00 = sleep
LIS_CTRL_REG1 = 0x20  # ODR[3:0]=0000 → power-down

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

def i2c_write8(addr, reg, val):
    i2c.writeto_mem(addr, reg, bytes([val]))

def sensors_sleep():
    i2c_write8(BME280_ADDR, BME_CTRL_MEAS, 0x00)  # BME → sleep
    i2c_write8(LIS3DH_ADDR, LIS_CTRL_REG1, 0x00)  # LIS → power-down
    # machine.deepsleep()  # далі — у deep-sleep
