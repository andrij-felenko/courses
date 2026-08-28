# 1. Перевірка: чи це той чіп?
if readReg(REG_WHO) != EXPECTED_ID:
    # біда з дротами або адресою — далі не йти
    return

# 2. Налаштування (раз при старті):
writeReg(REG_PWR, 0x00)                        # вийти зі сну
c = readReg(REG_CFG)                           # читай-зміни-запиши:
writeReg(REG_CFG, (c & ~0x18) | (0b10 << 3))   # діапазон AFS = ±8g

# 3. Читання виміру осі X (у головному циклі):
hi = readReg(REG_XOUT_H)
lo = readReg(REG_XOUT_H + 1)                   # сусідня комірка 0x3C
raw = int.from_bytes([hi, lo], "big", signed=True)  # склали два байти в знакове число
ax = raw / 4096.0                              # сирий відлік → g (±8g → 4096 LSB/g)
