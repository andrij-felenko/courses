from machine import I2C

MAX17048_ADDR = 0x36   # 7-бітна адреса в шині
REG_VCELL     = 0x02   # напруга комірки, 2 байти
REG_SOC       = 0x04   # стан заряду, 2 байти

def reg_read_u16(i2c, reg):
    # прочитати 2 байти з регістра reg й зібрати їх у 16-бітне
    # ціле зі старшим байтом попереду (big-endian чипа)
    b = i2c.readfrom_mem(MAX17048_ADDR, reg, 2)
    return (b[0] << 8) | b[1]               # старший байт — перший

def max17048_soc(i2c):
    # SoC у відсотках: регістр має роздільність 1/256 %
    return reg_read_u16(i2c, REG_SOC) / 256.0

def max17048_vcell(i2c):
    # напруга комірки у вольтах: крок АЦП 78.125 мкВ на молодший біт
    return reg_read_u16(i2c, REG_VCELL) * 78.125e-6
