// Оцінка тривалості читання N байтів з регістра давача по I2C.
// Послідовність: S · (адр+W) · (№рег) · Sr · (адр+R) · N байтів даних · P
function i2cReadTicks(nBytes) {
    const bytes  = 1 + 1 + 1 + nBytes;   // адр+W, №рег, адр+R, дані
    let   clocks = bytes * 9;            // 9 тактів на кожен байт (8 даних + ACK)
    clocks += 3;                         // S + Sr + P ≈ по одному такту
    return clocks;
}

// За скільки часу це пройде на стандартних 100 кГц?
//   1 такт = 1 / 100000 с = 10 мкс
function i2cReadMicros(nBytes) {
    return i2cReadTicks(nBytes) * 10;   // мкс
}
