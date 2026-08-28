#include <stdint.h>
#include <stddef.h>

#define CRC8_POLYNOMIAL 0x31
#define CRC8_INIT_VAL   0xFF

/* Побітовий алгоритм: мінімальний розмір коду (ROM), оптимальний для мікроконтролерів із малим Flash */
uint8_t sensor_calculate_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = CRC8_INIT_VAL;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (uint8_t)((crc << 1) ^ CRC8_POLYNOMIAL);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}
