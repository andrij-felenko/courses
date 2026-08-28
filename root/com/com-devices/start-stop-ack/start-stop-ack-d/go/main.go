// Оцінка тривалості читання N байтів з регістра давача по I2C.
// Послідовність: S · (адр+W) · (№рег) · Sr · (адр+R) · N байтів даних · P
func i2cReadTicks(nBytes uint32) uint32 {
    bytes := uint32(1) + 1 + 1 + nBytes // адр+W, №рег, адр+R, дані
    clocks := bytes * 9                 // 9 тактів на кожен байт (8 даних + ACK)
    clocks += 3                         // S + Sr + P ≈ по одному такту
    return clocks
}

// За скільки часу це пройде на стандартних 100 кГц?
//   1 такт = 1 / 100000 с = 10 мкс
func i2cReadMicros(nBytes uint32) uint32 {
    return i2cReadTicks(nBytes) * 10 // мкс
}
