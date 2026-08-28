#include <stdint.h>
#include <stddef.h>

static inline unsigned rtp_version(const uint8_t *p) { return  p[0] >> 6; }
static inline unsigned rtp_padding(const uint8_t *p) { return (p[0] >> 5) & 1; }
static inline unsigned rtp_ext(const uint8_t *p)     { return (p[0] >> 4) & 1; }
static inline unsigned rtp_cc(const uint8_t *p)      { return  p[0] & 0x0F; }
static inline unsigned rtp_marker(const uint8_t *p)  { return  p[1] >> 7; }
static inline unsigned rtp_pt(const uint8_t *p)      { return  p[1] & 0x7F; }

static inline uint16_t rtp_seq(const uint8_t *p) {
    return (uint16_t)((uint32_t)p[2] << 8 | p[3]);
}
static inline uint32_t rtp_ts(const uint8_t *p) {
    return (uint32_t)p[4] << 24 | (uint32_t)p[5] << 16 | (uint32_t)p[6] << 8 | p[7];
}
static inline uint32_t rtp_ssrc(const uint8_t *p) {
    return (uint32_t)p[8] << 24 | (uint32_t)p[9] << 16 | (uint32_t)p[10] << 8 | p[11];
}

/* Зміщення навантаження; 0 — пакет обірваний або зіпсований. */
static size_t rtp_payload_offset(const uint8_t *p, size_t len) {
    if (len < 12 || rtp_version(p) != 2) return 0;
    size_t off = 12 + 4 * (size_t)rtp_cc(p);
    if (off > len) return 0;
    if (rtp_ext(p)) {
        if (off + 4 > len) return 0;
        size_t words = (size_t)p[off + 2] << 8 | p[off + 3];
        off += 4 + 4 * words;
    }
    return off <= len ? off : 0;
}
