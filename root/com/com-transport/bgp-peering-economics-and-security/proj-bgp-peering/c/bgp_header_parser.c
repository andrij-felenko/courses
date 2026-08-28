/* bgp_header_parser.c — Парсер заголовка BGP на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <arpa/inet.h>

#define BGP_HEADER_LEN 19
#define BGP_MARKER_LEN 16

typedef struct {
    uint8_t  marker[BGP_MARKER_LEN];
    uint16_t length;
    uint8_t  type;
} __attribute__((packed)) bgp_header_t;

int parse_bgp_header(const uint8_t *buffer, size_t buf_len, bgp_header_t *out_hdr) {
    if (buf_len < BGP_HEADER_LEN) {
        return -1; /* Занадто короткий буфер */
    }

    memcpy(out_hdr, buffer, BGP_HEADER_LEN);
    out_hdr->length = ntohs(out_hdr->length);

    /* Перевірка кожної позиції маркера (усі байти мусять бути 0xFF) */
    for (int i = 0; i < BGP_MARKER_LEN; ++i) {
        if (out_hdr->marker[i] != 0xFF) {
            return -2; /* Збій синхронізації маркера */
        }
    }

    if (out_hdr->length < BGP_HEADER_LEN || out_hdr->length > 4096) {
        return -3; /* Вихід за межі нормативної довжини BGP-пакета */
    }

    return 0; /* Успішно розібрано */
}

int main(void) {
    /* Тестовий кадр BGP KEEPALIVE (19 байтів) */
    uint8_t raw_pkt[19] = {
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        0x00, 0x13, /* Length: 19 байтів */
        0x04        /* Type: 4 (KEEPALIVE) */
    };

    bgp_header_t hdr;
    int res = parse_bgp_header(raw_pkt, sizeof(raw_pkt), &hdr);
    if (res == 0) {
        printf("[C] BGP Packet Valid! Length: %u, Type: %u\n", hdr.length, hdr.type);
    } else {
        printf("[C] BGP Header Invalid: error code %d\n", res);
    }
    return 0;
}
