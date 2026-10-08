#include <stdint.h>
#include <stdbool.h>
#include <esp_log.h>

static const char *TAG = "AHT20_CRC";

// Обчислення контрольної суми CRC8 для давача AHT20
// Поліном: X^8 + X^5 + X^4 + 1 (0x31), початкове значення: 0xFF
uint8_t aht20_calculate_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ 0x31);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

// Перевірка та фільтрація 7-байтного пакунка AHT20
bool aht20_process_frame(const uint8_t buffer[7], float *humidity, float *temperature) {
    uint8_t calculated_crc = aht20_calculate_crc8(buffer, 6);
    uint8_t received_crc = buffer[6];

    if (calculated_crc != received_crc) {
        ESP_LOGW(TAG, "Помилка CRC8! Обчислено: 0x%02X, отримано: 0x%02X", calculated_crc, received_crc);
        return false;
    }

    // Декодування 20-бітного значення вологості (байти 1, 2 та старші 4 біти байта 3)
    uint32_t raw_humidity = ((uint32_t)buffer[1] << 12) | ((uint32_t)buffer[2] << 4) | ((uint32_t)buffer[3] >> 4);
    *humidity = ((float)raw_humidity / 1048576.0f) * 100.0f;

    // Декодування 20-бітного значення температури (молодші 4 біти байта 3, байти 4 та 5)
    uint32_t raw_temp = (((uint32_t)buffer[3] & 0x0F) << 16) | ((uint32_t)buffer[4] << 8) | (uint32_t)buffer[5];
    *temperature = ((float)raw_temp / 1048576.0f) * 200.0f - 50.0f;

    return true;
}
