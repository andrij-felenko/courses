#include <stdint.h>

struct proxy_hdr_v2 {
    uint8_t sig[12];  /* \x0D \x0A \x0D \x0A \x00 \x0D \x0A \x51 \x55 \x49 \x54 \x0A */
    uint8_t ver_cmd;  /* старші 4 біти: 0x20 (v2), молодші 4 біти: 0x01 (PROXY) */
    uint8_t fam_tr;   /* старші 4 біти: 0x10 (INET) / 0x20 (INET6), молодші: 0x01 (STREAM) */
    uint16_t len;     /* довжина адресної структури та векторів TLV у байтах */
    union {
        struct {
            uint32_t src_addr;
            uint32_t dst_addr;
            uint16_t src_port;
            uint16_t dst_port;
        } ipv4;
        struct {
            uint8_t  src_addr[16];
            uint8_t  dst_addr[16];
            uint16_t src_port;
            uint16_t dst_port;
        } ipv6;
        struct {
            uint8_t  src_addr[108];
            uint8_t  dst_addr[108];
        } unix_sock;
    } addr;
};
