#include <stdint.h>

typedef struct { const uint8_t *p; uint32_t len; } nalu_t;

// 0 — розібрано, −1 — запис пошкоджений.
// nal_len дістає розмір префікса довжини, яким у зразках доріжки відділено кадри.
// Інваріант усіх перевірок: i <= n, тож віднімання n - i не переповнюється.
static int take_list(const uint8_t *b, uint32_t n, uint32_t *i,
                     uint32_t want, nalu_t *out, uint32_t cap, uint32_t *got)
{
    *got = 0;
    for (uint32_t k = 0; k < want; k++) {
        if (n - *i < 2) return -1;
        uint32_t sz = ((uint32_t)b[*i] << 8) | b[*i + 1];  // старший байт першим
        *i += 2;
        if (n - *i < sz) return -1;
        if (*got < cap) out[(*got)++] = (nalu_t){ b + *i, sz };
        *i += sz;
    }
    return 0;
}

int avcc_parse(const uint8_t *b, uint32_t n,
               nalu_t *sps, uint32_t cap_sps, uint32_t *n_sps,
               nalu_t *pps, uint32_t cap_pps, uint32_t *n_pps,
               uint32_t *nal_len)
{
    if (n < 7 || b[0] != 0x01) return -1;   // інших версій запису не існує

    *nal_len = (b[4] & 0x03) + 1;           // 1, 2 або 4 байти
    if (*nal_len == 3) return -1;           // трибайтний префікс заборонено

    uint32_t i = 5;
    uint32_t want = b[i++] & 0x1F;          // число SPS — лише п'ять молодших бітів
    if (take_list(b, n, &i, want, sps, cap_sps, n_sps) < 0) return -1;

    if (i >= n) return -1;
    want = b[i++];                          // число PPS — цілий байт, без маски
    if (take_list(b, n, &i, want, pps, cap_pps, n_pps) < 0) return -1;

    return 0;                               // хвіст, якщо i < n, читають окремо
}
