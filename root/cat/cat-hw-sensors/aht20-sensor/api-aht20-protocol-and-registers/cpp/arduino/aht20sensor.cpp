#include <Wire.h>

#define AHT20_I2C_ADDR       0x38
#define AHT20_CMD_INIT       0xBE
#define AHT20_CMD_TRIGGER    0xAC

class AHT20Sensor {
public:
    static uint8_t calculateCRC8(const uint8_t *data, uint8_t len) {
        uint8_t crc = 0xFF;
        for (uint8_t i = 0; i < len; i++) {
            crc ^= data[i];
            for (uint8_t bit = 0; bit < 8; bit++) {
                if (crc & 0x80) {
                    crc = (crc << 1) ^ 0x31;
                } else {
                    crc = (crc << 1);
                }
            }
        }
        return crc;
    }

    bool begin() {
        Wire.begin();
        Wire.requestFrom((uint8_t)AHT20_I2C_ADDR, (uint8_t)1);
        if (!Wire.available()) return false;

        uint8_t status = Wire.read();
        if ((status & 0x08) == 0) { // Перевірка біта Calibrated
            Wire.beginTransmission(AHT20_I2C_ADDR);
            Wire.write(AHT20_CMD_INIT);
            Wire.write(0x08);
            Wire.write(0x00);
            if (Wire.endTransmission() != 0) return false;
            delay(10);
        }
        return true;
    }

    bool readData(float &humidity, float &temperature) {
        Wire.beginTransmission(AHT20_I2C_ADDR);
        Wire.write(AHT20_CMD_TRIGGER);
        Wire.write(0x33);
        Wire.write(0x00);
        if (Wire.endTransmission() != 0) return false;

        delay(80); // Очікування завершення АЦП-перетворення

        uint8_t buf[7];
        uint8_t bytesRead = Wire.requestFrom((uint8_t)AHT20_I2C_ADDR, (uint8_t)7);
        if (bytesRead < 7) return false;

        for (uint8_t i = 0; i < 7; i++) {
            buf[i] = Wire.read();
        }

        // Перевірка зайнятості
        if (buf[0] & 0x80) return false;

        // Валідація контрольної суми CRC8
        if (calculateCRC8(buf, 6) != buf[6]) return false;

        // Розпакування 20-бітних даних
        uint32_t rawRH = ((uint32_t)buf[1] << 12) | ((uint32_t)buf[2] << 4) | ((uint32_t)buf[3] >> 4);
        uint32_t rawTemp = (((uint32_t)buf[3] & 0x0F) << 16) | ((uint32_t)buf[4] << 8) | (uint32_t)buf[5];

        humidity = ((float)rawRH / 1048576.0f) * 100.0f;
        temperature = ((float)rawTemp / 1048576.0f) * 200.0f - 50.0f;

        return true;
    }
};
