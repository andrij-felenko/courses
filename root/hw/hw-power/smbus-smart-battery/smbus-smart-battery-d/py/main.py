from smbus2 import SMBus

# SMBus Read Word: код 0x09 → два байти LSB-перший
BATT_ADDR7 = 0x0B
cmd = 0x09                      # Voltage()

with SMBus(1) as bus:
    mv = bus.read_word_data(BATT_ADDR7, cmd)  # smbus2 сам збирає LSB-перший
# для сирого запиту {0x24, 0x1F} → mv = 0x1F24 = 7972

volts = mv / 1000.0             # одиниця регістра — мілівольти
# volts ≈ 7.97 В  → двобанковий Li-ion пакет
