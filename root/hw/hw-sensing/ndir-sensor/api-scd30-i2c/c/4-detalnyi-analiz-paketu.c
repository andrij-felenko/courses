#include <stdint.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    float co2_ppm;
    float temperature_c;
    float relative_humidity_pct;
} scd30_raw_measurement_t;

/**
 * @brief Повний парсинг та валідація 18-байтового фрейму SCD30.
 * @param rx_buf Буфер із 18 отриманими байтами.
 * @param out_meas Вказівник на структуру для збереження результатів.
 * @return 0 при успіху, -1 при помилці валідації CRC.
 */
int scd30_unpack_measurement_frame(const uint8_t rx_buf[18], scd30_raw_measurement_t *out_meas) {
    // Перевірка цілісності всіх 6 контрольних сум CRC-8
    for (size_t i = 0; i < 6; ++i) {
        uint8_t calculated_crc = scd30_compute_crc8(&rx_buf[i * 3], 2);
        if (calculated_crc != rx_buf[i * 3 + 2]) {
            return -1; // Пакет пошкоджено завадами на шині
        }
    }

    // Реконструкція 32-бітних слів Big-Endian
    uint32_t raw_co2 = ((uint32_t)rx_buf[0] << 24) |
                       ((uint32_t)rx_buf[1] << 16) |
                       ((uint32_t)rx_buf[3] << 8)  |
                       ((uint32_t)rx_buf[4]);

    uint32_t raw_temp = ((uint32_t)rx_buf[6] << 24) |
                        ((uint32_t)rx_buf[7] << 16) |
                        ((uint32_t)rx_buf[9] << 8)  |
                        ((uint32_t)rx_buf[10]);

    uint32_t raw_rh = ((uint32_t)rx_buf[12] << 24) |
                      ((uint32_t)rx_buf[13] << 16) |
                      ((uint32_t)rx_buf[15] << 8)  |
                      ((uint32_t)rx_buf[16]);

    // Копіювання у пам'ять float (IEEE-754) без порушення strict-aliasing
    memcpy(&out_meas->co2_ppm, &raw_co2, sizeof(float));
    memcpy(&out_meas->temperature_c, &raw_temp, sizeof(float));
    memcpy(&out_meas->relative_humidity_pct, &raw_rh, sizeof(float));

    return 0;
}
