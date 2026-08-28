#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

bool pms5003_verify_frame(const uint8_t *buffer, size_t len) {
    if (!buffer || len < 32) return false;

    // Перевірка преамбули 0x42 0x4D та довжини 0x001C (28)
    if (buffer[0] != 0x42 || buffer[1] != 0x4D) return false;
    uint16_t frame_len = (uint16_t)((buffer[2] << 8) | buffer[3]);
    if (frame_len != 28) return false;

    uint16_t calc_sum = 0;
    for (size_t i = 0; i < 30; ++i) {
        calc_sum += buffer[i];
    }

    uint16_t rx_sum = (uint16_t)((buffer[30] << 8) | buffer[31]);
    return (calc_sum == rx_sum);
}
