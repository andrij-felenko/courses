// CRC-4 для PROM MS5611 (алгоритм TE Connectivity, AN520).
// Приймає масив 8 слів; повертає true, якщо обчислена сума збіглася із зашитою.
bool ms5611_prom_crc_ok(uint16_t *prom) {
  uint16_t n_rem = 0x00;               // робочий 16-бітний залишок (CRC-регістр)
  uint16_t crc_read = prom[7];         // запам'ятати слово з зашитою сумою
  uint8_t  crc_expected = prom[7] & 0x000F;   // сама CRC-4 — молодший нібл

  prom[7] = prom[7] & 0xFF00;          // занулити нібл суми ПЕРЕД обчисленням

  for (uint8_t cnt = 0; cnt < 16; cnt++) {     // 16 байтів = 8 слів
    if (cnt % 2 == 1)
      n_rem ^= (uint16_t)(prom[cnt >> 1] & 0x00FF);   // непарний крок — молодший байт
    else
      n_rem ^= (uint16_t)(prom[cnt >> 1] >> 8);       // парний крок — старший байт

    for (uint8_t bit = 8; bit > 0; bit--) {
      if (n_rem & 0x8000)
        n_rem = (n_rem << 1) ^ 0x3000;    // старший біт = 1 → зсув + XOR з поліномом
      else
        n_rem = (n_rem << 1);             // інакше просто зсув
    }
  }

  n_rem = (n_rem >> 12) & 0x000F;      // готова CRC-4 — старші 4 біти залишку
  prom[7] = crc_read;                  // відновити слово (ми його псували маскою)

  return (n_rem == crc_expected);
}
