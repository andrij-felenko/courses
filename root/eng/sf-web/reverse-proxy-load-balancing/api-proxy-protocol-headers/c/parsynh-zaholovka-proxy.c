#include <stdio.h>
#include <string.h>
#include <arpa/inet.h>

static const uint8_t PROXY_V2_SIG[12] = {
    0x0D, 0x0A, 0x0D, 0x0A, 0x00, 0x0D, 0x0A, 0x51, 0x55, 0x49, 0x54, 0x0A
};

int parse_proxy_v2(const uint8_t *buf, size_t buf_len, char *src_ip_out, uint16_t *src_port_out) {
    if (buf_len < 16) return -1; /* Замалий буфер для базового заголовка */

    /* 1. Перевірка 12-байтної сигнатури */
    if (memcmp(buf, PROXY_V2_SIG, 12) != 0) return -1;

    /* 2. Перевірка версії (мусить бути 2) */
    uint8_t ver = (buf[12] >> 4) & 0x0F;
    if (ver != 2) return -1;

    uint8_t cmd = buf[12] & 0x0F;
    if (cmd == 0x00) {
        /* LOCAL з'єднання: адреса не передається */
        return 0;
    } else if (cmd != 0x01) {
        return -1; /* Невідома команда */
    }

    uint8_t fam = (buf[13] >> 4) & 0x0F;
    uint16_t payload_len = ntohs(*(const uint16_t *)(buf + 14));
    if (buf_len < 16 + payload_len) return -1; /* Неповні дані */

    const struct proxy_hdr_v2 *hdr = (const struct proxy_hdr_v2 *)buf;

    if (fam == 0x01) { /* IPv4 */
        struct in_addr in;
        in.s_addr = hdr->addr.ipv4.src_addr;
        inet_ntop(AF_INET, &in, src_ip_out, INET_ADDRSTRLEN);
        *src_port_out = ntohs(hdr->addr.ipv4.src_port);
        return 1;
    } else if (fam == 0x02) { /* IPv6 */
        inet_ntop(AF_INET6, hdr->addr.ipv6.src_addr, src_ip_out, INET6_ADDRSTRLEN);
        *src_port_out = ntohs(hdr->addr.ipv6.src_port);
        return 1;
    }

    return 0;
}
