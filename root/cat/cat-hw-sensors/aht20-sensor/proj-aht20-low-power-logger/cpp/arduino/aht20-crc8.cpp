#include <Wire.h>

#define I2C_SDA_PIN      21
#define I2C_SCL_PIN      22
#define AHT20_ADDR       0x38
#define SLEEP_SEC        60

// Змінні у пам'яті RTC зберігають значення між циклами сну
RTC_DATA_ATTR uint32_t boot_count = 0;
RTC_DATA_ATTR float last_temp = 0.0f;
RTC_DATA_ATTR float last_hum = 0.0f;

uint8_t aht20_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++) {
            crc = (crc & 0x80) ? ((crc << 1) ^ 0x31) : (crc << 1);
        }
    }
    return crc;
}

void setup() {
    boot_count++;
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, 100000);

    // Запуск перетворення AHT20
    Wire.beginTransmission(AHT20_ADDR);
    Wire.write(0xAC);
    Wire.write(0x33);
    Wire.write(0x00);
    Wire.endTransmission();

    // Легкий сон 80 мс замість блокуючого delay() для зниження струму до 1 мА
    esp_sleep_enable_timer_wakeup(80ULL * 1000ULL);
    esp_light_sleep_start();

    // Зчитування 7 байтів результату
    if (Wire.requestFrom(AHT20_ADDR, 7) == 7) {
        uint8_t rx[7];
        for (int i = 0; i < 7; i++) {
            rx[i] = Wire.read();
        }

        // Перевірка готовності (біт 7 == 0) та валідності CRC
        if (!(rx[0] & 0x80) && (aht20_crc8(rx, 6) == rx[6])) {
            uint32_t raw_hum = (((uint32_t)rx[1] << 16) | ((uint32_t)rx[2] << 8) | rx[3]) >> 4;
            uint32_t raw_temp = (((uint32_t)(rx[3] & 0x0F) << 16) | ((uint32_t)rx[4] << 8) | rx[5]);

            last_hum = ((float)raw_hum / 1048576.0f) * 100.0f;
            last_temp = ((float)raw_temp / 1048576.0f) * 200.0f - 50.0f;
        }
    }

    // Закриття шини та налаштування Deep Sleep
    Wire.end();
    esp_sleep_enable_timer_wakeup((uint64_t)SLEEP_SEC * 1000000ULL);
    esp_deep_sleep_start();
}

void loop() {
    // Порожній цикл: виконання ніколи не доходить сюди через Deep Sleep
}
