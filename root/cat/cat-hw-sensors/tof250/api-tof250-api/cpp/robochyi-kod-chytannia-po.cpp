#include <Wire.h>

#define TOF_ADDR  0x52    // 7-бітна адреса (байт 0xA4 → 0x52 у Wire)
#define REG_DIST  0x00    // відстань, 2 байти (сира чи згладжена — за режимом s3-x#)

// Прочитати 16-бітну відстань із регістра 0x00. -1 = помилка.
int tofReadDistance() {
    Wire.beginTransmission(TOF_ADDR);
    Wire.write(REG_DIST);                   // «хочу читати з регістра 0x00»
    if (Wire.endTransmission(false) != 0)   // повторний старт, шину НЕ відпускаємо
        return -1;                          // модуль не підтвердив адресу

    if (Wire.requestFrom(TOF_ADDR, (uint8_t)2) != 2)
        return -1;                          // не дочекались двох байтів

    uint16_t hi = Wire.read();              // старший байт приходить першим
    uint16_t lo = Wire.read();              // потім молодший
    return (int)((hi << 8) | lo);           // склали → відстань у мм
}
