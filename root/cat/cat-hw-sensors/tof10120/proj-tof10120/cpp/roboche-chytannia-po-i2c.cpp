#include <Wire.h>

#define TOF_ADDR   0x52     // 7-бітна адреса (байт 0xA4 → 0x52)
#define REG_RAW    0x00     // миттєва (сира) відстань, 2 байти MSB-first
#define REG_FILT   0x04     // згладжена відстань, 2 байти MSB-first

// Повертає відстань у мм (0..~1993) або -1, якщо модуль не відповів як слід.
int tofReadReg(uint8_t reg) {
    Wire.beginTransmission(TOF_ADDR);
    Wire.write(reg);                       // куди поставити внутрішній вказівник
    if (Wire.endTransmission(false) != 0)  // repeated-start: не відпускаємо шину
        return -1;                         // ніхто не підтвердив адресу → нема модуля

    if (Wire.requestFrom(TOF_ADDR, (uint8_t)2) != 2)
        return -1;                         // прийшло менше двох байтів → збій обміну

    uint16_t hi = Wire.read();             // старший байт
    uint16_t lo = Wire.read();             // молодший байт
    return (int)((hi << 8) | lo);          // склали 16-бітне число, мм
}

void setup() {
    Wire.begin();                          // на ESP32/STM32/Pico тут задайте свої ніжки
    Serial.begin(115200);
}

void loop() {
    int mm = tofReadReg(REG_FILT);         // згладжена; для сирої — REG_RAW
    if (mm < 0)        Serial.println("TOF: нема відповіді");
    else if (mm == 0)  Serial.println("TOF: 0 (ціль надто близько / поза діапазоном?)");
    else { Serial.print(mm); Serial.println(" мм"); }
    delay(100);
}
