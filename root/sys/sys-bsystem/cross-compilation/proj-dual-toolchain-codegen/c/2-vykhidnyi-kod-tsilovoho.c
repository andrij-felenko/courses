#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

extern const uint32_t g_crc32_lookup[256];

uint32_t calculate_buffer_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        uint8_t table_index = (uint8_t)((crc ^ data[i]) & 0xFFU);
        crc = (crc >> 8U) ^ g_crc32_lookup[table_index];
    }
    return crc ^ 0xFFFFFFFFU;
}

int main(void) {
    const uint8_t payload[] = "Firmware telemetry packet payload";
    uint32_t checksum = calculate_buffer_crc32(payload, sizeof(payload) - 1);
    printf("Обчислена контрольна сума CRC-32: 0x%08X\n", checksum);
    return 0;
}
