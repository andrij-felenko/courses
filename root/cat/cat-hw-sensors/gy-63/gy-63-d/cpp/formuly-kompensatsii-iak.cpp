// поправки другого порядку (у цілій арифметиці)
if (TEMP < 2000) {                       // нижче 20 °C
    int64_t t2 = (int64_t)dT * dT >> 31;
    int64_t off2  = 5 * (int64_t)(TEMP - 2000) * (TEMP - 2000) / 2;
    int64_t sens2 = 5 * (int64_t)(TEMP - 2000) * (TEMP - 2000) / 4;
    if (TEMP < -1500) {                   // нижче −15 °C — ще сильніше
        off2  += 7 * (int64_t)(TEMP + 1500) * (TEMP + 1500);
        sens2 += 11 * (int64_t)(TEMP + 1500) * (TEMP + 1500) / 2;
    }
    TEMP -= t2;
    OFF  -= off2;
    SENS -= sens2;
}
