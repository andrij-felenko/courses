// Оцінка тривалості читання N байтів з регістра давача по I2C.
// Послідовність: S · (адр+W) · (№рег) · Sr · (адр+R) · N байтів даних · P
uint32_t i2c_read_ticks(uint32_t n_bytes) {
    uint32_t bytes  = 1 /*адр+W*/ + 1 /*№рег*/ + 1 /*адр+R*/ + n_bytes;
    uint32_t clocks = bytes * 9;     // 9 тактів на кожен байт (8 даних + ACK)
    clocks += 3;                     // S + Sr + P ≈ по одному такту
    return clocks;
}

// За скільки часу це пройде на стандартних 100 кГц?
//   1 такт = 1 / 100000 с = 10 мкс
uint32_t i2c_read_micros(uint32_t n_bytes) {
    return i2c_read_ticks(n_bytes) * 10;   // мкс
}
