// SMBus Read Word: код 0x09 → два байти LSB-перший
const battAddr7 = 0x0B
const cmd = 0x09 // Voltage()

raw, err := dev.ReadWordData(cmd) // raw[0]=молодший, raw[1]=старший
if err != nil {
    log.Fatal(err)
}

mv := uint16(raw[0]) | uint16(raw[1])<<8
// raw = {0x24, 0x1F} → mv = 0x24 | (0x1F << 8) = 0x1F24 = 7972

volts := float64(mv) / 1000.0 // одиниця регістра — мілівольти
// volts ≈ 7.97 В  → двобанковий Li-ion пакет
