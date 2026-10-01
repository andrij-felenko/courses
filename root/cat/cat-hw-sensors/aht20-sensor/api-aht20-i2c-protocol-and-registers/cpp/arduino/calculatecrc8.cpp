#include <Wire.h>

const uint8_t AHT20_I2C_ADDR      = 0x38;
const uint8_t AHT20_CMD_TRIGGER   = 0xAC;
const uint8_t AHT20_CMD_INIT      = 0xBE;
const uint8_t AHT20_CMD_SOFTRESET = 0xBA;

// Обчислення контрольної суми CRC-8 за поліномом 0x31
uint8_t calculateCRC8(const uint8_t *data, uint8_t len) {
    uint8_t crc = 0xFF;
    for (uint8_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

bool readAHT20(float &humidity, float &temperature) {
    // 1. Відправка тригера вимірювання (0xAC, 0x33, 0x00)
    Wire.beginTransmission(AHT20_I2C_ADDR);
    Wire.write(AHT20_CMD_TRIGGER);
    Wire.write(0x33);
    Wire.write(0x00);
    if (Wire.endTransmission() != 0) {
        return false; // Помилка на шині I2C
    }

    // 2. Пауза 80 мс на виконання перетворення АЦП
    delay(80);

    // 3. Зчитування 7 байтів відповіді
    if (Wire.requestFrom(AHT20_I2C_ADDR, (uint8_t)7) != 7) {
        return false;
    }

    uint8_t data[7];
    for (uint8_t i = 0; i < 7; i++) {
        data[i] = Wire.read();
    }

    // 4. Перевірка статусу: Busy bit[7] та Calibrated bit[3]
    uint8_t status = data[0];
    if (status & 0x80) { // Busy bit[7] == 1
        return false; // Давач ще зайнятий
    }
    if (!(status & 0x08)) { // Calibrated bit[3] == 0
        return false; // Потрібна ініціалізація 0xBE
    }

    // 5. Перевірка цілісності даних через CRC-8
    if (calculateCRC8(data, 6) != data[6]) {
        return false; // Помилка контрольної суми
    }

    // 6. Декодування 20-бітних даних
    uint32_t rawHumidity = ((uint32_t)data[1] << 12) | ((uint32_t)data[2] << 4) | (data[3] >> 4);
    uint32_t rawTemp = (((uint32_t)data[3] & 0x0F) << 16) | ((uint32_t)data[4] << 8) | data[5];

    humidity = ((float)rawHumidity / 1048576.0f) * 100.0f;
    temperature = ((float)rawTemp / 1048576.0f) * 200.0f - 50.0f;

    return true;
}
