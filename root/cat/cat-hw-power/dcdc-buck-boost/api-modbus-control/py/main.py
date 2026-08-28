# pip install minimalmodbus   (тягне за собою pyserial)
# minimalmodbus ховає збирання кадру Modbus RTU і CRC-16.
import time
import minimalmodbus

# Адреси регістрів (0-базовані) — з мапи DPS/DPH.
REG_USET  = 0x00   # задана напруга,   вольти × 100
REG_ISET  = 0x01   # заданий струм,    ампери × 1000  (!! інший множник)
REG_UOUT  = 0x02   # виміряна напруга, вольти × 100
REG_IOUT  = 0x03   # виміряний струм,  ампери × 1000
REG_ONOFF = 0x09   # вмикач виходу,    0 / 1

# 1. Відкриваємо порт. Slave ID = 1. Далі задаємо 9600 8N1.
#    Порт: "/dev/ttyUSB0" на Linux, "COM4" на Windows.
dps = minimalmodbus.Instrument("/dev/ttyUSB0", 1)   # (порт, адреса веденого)
dps.serial.baudrate = 9600
dps.serial.bytesize = 8
dps.serial.parity   = minimalmodbus.serial.PARITY_NONE
dps.serial.stopbits = 1
dps.serial.timeout  = 0.5   # секунди

# 2. Пишемо задані значення.
#    numberOfDecimals робить кодування за нас: бібліотека САМА множить
#    на 10**decimals. Тому напруга — 2 знаки (×100), струм — 3 знаки (×1000).
dps.write_register(REG_USET, 5.00,  numberOfDecimals=2)   # 5.00 В  -> шле 500
dps.write_register(REG_ISET, 1.000, numberOfDecimals=3)   # 1.000 А -> шле 1000

# 3. Вмикаємо вихід — БЕЗ цього на клемах нуль.
dps.write_register(REG_ONOFF, 1)

time.sleep(1)  # даємо виходу встановитися

# 4. Читаємо вимір. Ті самі decimals повертають людські числа.
u = dps.read_register(REG_UOUT, numberOfDecimals=2)   # вольти
i = dps.read_register(REG_IOUT, numberOfDecimals=3)   # ампери
print(f"на виході: {u:.2f} В, {i:.3f} А")
