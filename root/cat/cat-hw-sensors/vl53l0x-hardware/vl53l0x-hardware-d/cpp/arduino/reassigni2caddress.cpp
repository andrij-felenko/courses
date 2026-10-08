#include <Wire.h>

const uint8_t PIN_XSHUT_1 = 4;
const uint8_t PIN_XSHUT_2 = 5;

const uint8_t ADDR_DEFAULT = 0x29;
const uint8_t ADDR_SENSOR_1 = 0x30;
const uint8_t ADDR_SENSOR_2 = 0x31;
const uint8_t REG_SLAVE_ADDR = 0x8A;

bool reassignI2CAddress(uint8_t oldAddr, uint8_t newAddr) {
    Wire.beginTransmission(oldAddr);
    Wire.write(REG_SLAVE_ADDR);
    Wire.write(newAddr & 0x7F);
    return (Wire.endTransmission() == 0);
}

void setup() {
    Wire.begin();
    pinMode(PIN_XSHUT_1, OUTPUT);
    pinMode(PIN_XSHUT_2, OUTPUT);

    // Переведення вхідних ліній скидання в низький стан
    digitalWrite(PIN_XSHUT_1, LOW);
    digitalWrite(PIN_XSHUT_2, LOW);
    delay(10);

    // Ініціалізація та зміна адреси першого сенсора
    digitalWrite(PIN_XSHUT_1, HIGH);
    delay(5);
    reassignI2CAddress(ADDR_DEFAULT, ADDR_SENSOR_1);

    // Ініціалізація та зміна адреси другого сенсора
    digitalWrite(PIN_XSHUT_2, HIGH);
    delay(5);
    reassignI2CAddress(ADDR_DEFAULT, ADDR_SENSOR_2);
}

void loop() {
    // Основний цикл опитування сенсорів за новими адресами
}
