#include <Arduino.h>
#include <Wire.h>

// I2C адреса та команди AHT20
static constexpr uint8_t AHT20_I2C_ADDR = 0x38;
static constexpr uint8_t CMD_INIT = 0xBE;
static constexpr uint8_t CMD_MEASURE = 0xAC;
static constexpr uint8_t CMD_SOFT_RESET = 0xBA;

// Налаштування Deep Sleep (5 хвилин)
static constexpr uint64_t TIME_TO_SLEEP_US = 300ULL * 1000000ULL;

struct AHT20Data {
    float temperature;
    float humidity;
    bool valid;
};

class AHT20Sensor {
private:
    uint8_t calculateCRC8(const uint8_t* data, size_t len) {
        uint8_t crc = 0xFF;
        for (size_t i = 0; i < len; ++i) {
            crc ^= data[i];
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x80) {
                    crc = (crc << 1) ^ 0x31;
                } else {
                    crc <<= 1;
                }
            }
        }
        return crc;
    }

public:
    bool begin() {
        Wire.begin();
        Wire.beginTransmission(AHT20_I2C_ADDR);
        Wire.write(0x71);
        if (Wire.endTransmission() != 0) {
            return false;
        }

        Wire.requestFrom(AHT20_I2C_ADDR, static_cast<uint8_t>(1));
        if (Wire.available()) {
            uint8_t status = Wire.read();
            if ((status & 0x08) == 0) { // Перевірка прапорця Calibrated
                Wire.beginTransmission(AHT20_I2C_ADDR);
                Wire.write(CMD_INIT);
                Wire.write(0x08);
                Wire.write(0x00);
                Wire.endTransmission();
                delay(10);
            }
        }
        return true;
    }

    AHT20Data read() {
        AHT20Data result{0.0f, 0.0f, false};

        Wire.beginTransmission(AHT20_I2C_ADDR);
        Wire.write(CMD_MEASURE);
        Wire.write(0x33);
        Wire.write(0x00);
        if (Wire.endTransmission() != 0) {
            return result;
        }

        delay(80); // Виконання вимірювання чипом AHT20

        Wire.requestFrom(AHT20_I2C_ADDR, static_cast<uint8_t>(7));
        if (Wire.available() < 7) {
            return result;
        }

        uint8_t buf[7];
        for (int i = 0; i < 7; ++i) {
            buf[i] = Wire.read();
        }

        // Перевірка прапорця Busy
        if (buf[0] & 0x80) {
            return result;
        }

        // Перевірка контрольної суми CRC-8
        if (calculateCRC8(buf, 6) != buf[6]) {
            return result;
        }

        // Декодування 20-бітних сирих даних
        uint32_t rawHumidity = ((static_cast<uint32_t>(buf[1]) << 12) |
                                (static_cast<uint32_t>(buf[2]) << 4) |
                                (static_cast<uint32_t>(buf[3]) >> 4));

        uint32_t rawTemp = (((static_cast<uint32_t>(buf[3]) & 0x0F) << 16) |
                            (static_cast<uint32_t>(buf[4]) << 8) |
                            static_cast<uint32_t>(buf[5]));

        result.humidity = (static_cast<float>(rawHumidity) / 1048576.0f) * 100.0f;
        result.temperature = (static_cast<float>(rawTemp) / 1048576.0f) * 200.0f - 50.0f;
        result.valid = true;

        return result;
    }
};

class ClimateNode {
private:
    AHT20Sensor sensor;

public:
    void executeCycle() {
        if (!sensor.begin()) {
            Serial.println("Помилка підключення AHT20 по I2C!");
            enterDeepSleep();
            return;
        }

        AHT20Data data = sensor.read();
        if (data.valid) {
            Serial.printf("Температура: %.2f °C, Вологість: %.2f %%\n", data.temperature, data.humidity);
            // Імітація формування телеметричного пакета MQTT/BLE
        } else {
            Serial.println("Помилка цілісності даних CRC-8 або прапорця Busy!");
        }

        enterDeepSleep();
    }

    void enterDeepSleep() {
        Serial.println("Перехід у режим Deep Sleep на 5 хвилин...");
        esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP_US);
        esp_deep_sleep_start();
    }
};

ClimateNode node;

void setup() {
    Serial.begin(115200);
    delay(100);
    node.executeCycle();
}

void loop() {
    // Не використовується — керування передано Deep Sleep
}
