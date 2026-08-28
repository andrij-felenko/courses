#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    uint8_t  ver_ihl;       // Версія (4 біти) + IHL (4 біти)
    uint8_t  tos;
    uint16_t total_length;
    uint16_t packet_id;
    uint16_t flags_fragment;
    uint8_t  ttl;
    uint8_t  protocol;
    uint16_t header_checksum;
    uint32_t src_ip;
    uint32_t dst_ip;
} Ipv4HeaderC;

// Обчислення 16-бітної суми за RFC 1071
uint16_t calculate_checksum_c(const uint8_t* buffer, size_t len) {
    uint32_t sum = 0;
    for (size_t i = 0; i + 1 < len; i += 2) {
        uint16_t word;
        // Безпечне копіювання захищає від unaligned fault на ARM
        memcpy(&word, buffer + i, 2);
        sum += word;
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return (uint16_t)(~sum);
}
