// Результати останнього виміру (у людських одиницях).
float g_temperature_C;    // °C
float g_pressure_hPa;     // мбар = гПа

// Повний вимір: D1, D2, компенсація 1-го і 2-го порядку. true — успіх.
bool ms5611_measure() {
  uint32_t D1, D2;                              // сирі тиск і температура
  if (!ms5611_convert_read(CMD_CONV_D1, &D1)) return false;
  if (!ms5611_convert_read(CMD_CONV_D2, &D2)) return false;

  // Коефіцієнти для читабельності:
  uint16_t C1 = g_prom[1];   // чутливість (SENS_T1)
  uint16_t C2 = g_prom[2];   // зсув (OFF_T1)
  uint16_t C3 = g_prom[3];   // температурний коеф. чутливості (TCS)
  uint16_t C4 = g_prom[4];   // температурний коеф. зсуву (TCO)
  uint16_t C5 = g_prom[5];   // опорна температура (T_REF)
  uint16_t C6 = g_prom[6];   // температурний коеф. температури (TEMPSENS)

  // -- 1) температура (у сотих градуса) --
  int32_t dT   = (int32_t)D2 - ((int32_t)C5 << 8);            // D2 − C5·2⁸
  int32_t TEMP = 2000 + (int32_t)(((int64_t)dT * C6) >> 23);  // 20.00 °C = 2000

  // -- 2) зсув і чутливість, виправлені на температуру (ОБОВ'ЯЗКОВО 64 біти!) --
  int64_t OFF  = ((int64_t)C2 << 16) + (((int64_t)C4 * dT) >> 7);
  int64_t SENS = ((int64_t)C1 << 15) + (((int64_t)C3 * dT) >> 8);

  // -- 3) компенсація другого порядку (для холоду) --
  if (TEMP < 2000) {                                  // нижче 20 °C
    int64_t dT64 = dT;
    int64_t T2   = (dT64 * dT64) >> 31;
    int64_t d    = (int64_t)TEMP - 2000;
    int64_t OFF2  = (5 * d * d) >> 1;                 // 5·(TEMP−2000)² / 2
    int64_t SENS2 = (5 * d * d) >> 2;                 // 5·(TEMP−2000)² / 4
    if (TEMP < -1500) {                               // нижче −15 °C — ще сильніше
      int64_t e = (int64_t)TEMP + 1500;
      OFF2  += 7 * e * e;                             // + 7·(TEMP+1500)²
      SENS2 += (11 * e * e) >> 1;                     // + 11·(TEMP+1500)² / 2
    }
    TEMP -= (int32_t)T2;
    OFF  -= OFF2;
    SENS -= SENS2;
  }

  // -- 4) тиск (у сотих мілібара) --
  int32_t P = (int32_t)(((( (int64_t)D1 * SENS) >> 21) - OFF) >> 15);

  g_temperature_C = TEMP / 100.0f;      // 2007 → 20.07 °C
  g_pressure_hPa  = P    / 100.0f;      // 100009 → 1000.09 гПа
  return true;
}
