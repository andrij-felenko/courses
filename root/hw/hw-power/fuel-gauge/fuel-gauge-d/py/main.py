import smbus2

MAX17048_ADDR = 0x36   # 7-бітна адреса в шині
REG_VCELL     = 0x02   # напруга комірки, 2 байти
REG_SOC       = 0x04   # стан заряду, 2 байти

def reg_read_u16(bus, reg):
    # прочитати 2 байти з регістра reg й зібрати їх у 16-бітне
    # ціле зі старшим байтом попереду (big-endian чипа)
    hi, lo = bus.read_i2c_block_data(MAX17048_ADDR, reg, 2)
    return (hi << 8) | lo                   # старший байт — перший

def max17048_soc(bus):
    # SoC у відсотках: регістр має роздільність 1/256 %
    return reg_read_u16(bus, REG_SOC) / 256.0

def max17048_vcell(bus):
    # напруга комірки у вольтах: крок АЦП 78.125 мкВ на молодший біт
    return reg_read_u16(bus, REG_VCELL) * 78.125e-6
