raw, err := dev.ReadWordData(0x16) // BatteryStatus()
if err != nil {
    log.Fatal(err)
}
st := uint16(raw[0]) | uint16(raw[1])<<8

const (
    overTempAlarm   = 1 << 12
    terminateCharge = 1 << 14 // «годі заряджати»
    overCharged     = 1 << 15
)

if st&overTempAlarm != 0 {
    stopEverything() // перегрів — вимикаємо
}
if st&terminateCharge != 0 {
    chargerOff() // батарея каже: досить
}
