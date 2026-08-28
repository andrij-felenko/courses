#include <stdio.h>
#include <stdint.h>

void process_packet_header(const uint8_t *buffer) {
    // Помилка: припущення про Little-Endian у пам'яті
    uint32_t raw_id = *(const uint32_t *)buffer;

    // Надійна перевірка та конвертація з Big-Endian (Network Byte Order)
    #if defined(__GNUC__) || defined(__clang__)
    uint32_t id_le = __builtin_bswap32(raw_id);
    #else
    uint32_t id_le = ((raw_id >> 24) & 0xFF) |
                     ((raw_id >> 8)  & 0xFF00) |
                     ((raw_id << 8)  & 0xFF0000) |
                     ((raw_id << 24) & 0xFF000000);
    #endif

    (void)id_le;
}
