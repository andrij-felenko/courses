#include <stdint.h>
#include <string.h>

#define ROTL(x, n) (((x) << (n)) | ((x) >> (32 - (n))))

#define QR(a, b, c, d) do {          \
    a += b; d ^= a; d = ROTL(d, 16); \
    c += d; b ^= c; b = ROTL(b, 12); \
    a += b; d ^= a; d = ROTL(d, 8);  \
    c += d; b ^= c; b = ROTL(b, 7);  \
} while (0)

/* 64 байти псевдовипадкового потоку з ключа й номера блоку. */
static void chacha20_block(const uint8_t key[32], uint32_t counter, uint8_t out[64]) {
    uint32_t s[16];
    s[0] = 0x61707865; s[1] = 0x3320646e;      /* "expand 32-byte k" */
    s[2] = 0x79622d32; s[3] = 0x6b206574;
    for (int i = 0; i < 8; i++)                /* ключ — 8 слів, little-endian */
        s[4 + i] =  (uint32_t)key[4*i]
                 | ((uint32_t)key[4*i + 1] << 8)
                 | ((uint32_t)key[4*i + 2] << 16)
                 | ((uint32_t)key[4*i + 3] << 24);
    s[12] = counter; s[13] = 0; s[14] = 0; s[15] = 0;   /* лічильник + nonce=0 */

    uint32_t x[16];
    memcpy(x, s, sizeof x);
    for (int i = 0; i < 10; i++) {             /* 20 раундів = 10 подвійних */
        QR(x[0], x[4], x[ 8], x[12]);          /* чотири стовпці */
        QR(x[1], x[5], x[ 9], x[13]);
        QR(x[2], x[6], x[10], x[14]);
        QR(x[3], x[7], x[11], x[15]);
        QR(x[0], x[5], x[10], x[15]);          /* чотири діагоналі */
        QR(x[1], x[6], x[11], x[12]);
        QR(x[2], x[7], x[ 8], x[13]);
        QR(x[3], x[4], x[ 9], x[14]);
    }
    for (int i = 0; i < 16; i++) {
        uint32_t v = x[i] + s[i];              /* ← додавання вихідного стану */
        out[4*i]     = (uint8_t)(v);           /* серіалізація little-endian */
        out[4*i + 1] = (uint8_t)(v >> 8);
        out[4*i + 2] = (uint8_t)(v >> 16);
        out[4*i + 3] = (uint8_t)(v >> 24);
    }
}
