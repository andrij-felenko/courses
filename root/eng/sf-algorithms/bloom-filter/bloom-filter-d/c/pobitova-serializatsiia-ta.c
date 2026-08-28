#include <stdint.h>
#include <arpa/inet.h>

typedef struct __attribute__((packed)) {
    uint32_t magic;      /* 0x424C4F4F ("BLOO") */
    uint32_t version;    /* Версія 1 */
    uint64_t num_bits;   /* Кількість бітів m у Big-Endian */
    uint32_t num_hashes; /* Кількість хеш-функцій k у Big-Endian */
} bloom_net_header_t;

void serialize_header(bloom_net_header_t *hdr, uint64_t m, uint32_t k) {
    hdr->magic = htonl(0x424C4F4F);
    hdr->version = htonl(1);
    /* Перетворення у мережевий порядок байтів (Big-Endian) */
    hdr->num_bits = __builtin_bswap64(m);
    hdr->num_hashes = htonl(k);
}
