#include <cstdint>
#include <cstddef>
#include <array>
#include <vector>
#include <functional>

// ── читання з мережевого порядку байтів: старший байт іде першим ─────────────
static inline uint16_t rd16(const uint8_t* p) {
    return static_cast<uint16_t>(static_cast<uint32_t>(p[0]) << 8 | p[1]);
}
static inline uint32_t rd32(const uint8_t* p) {
    return static_cast<uint32_t>(p[0]) << 24 | static_cast<uint32_t>(p[1]) << 16
         | static_cast<uint32_t>(p[2]) <<  8 | static_cast<uint32_t>(p[3]);
}

struct RtpHeader {
    uint8_t  pt     = 0;
    bool     marker = false;
    uint16_t seq    = 0;
    uint32_t ts     = 0;
    uint32_t ssrc   = 0;
    const uint8_t* payload = nullptr;
    size_t         payload_len = 0;
};

bool parse_rtp(const uint8_t* buf, size_t n, RtpHeader& h) {
    if (n < 12)            return false;   // навіть на заголовок не вистачає
    if ((buf[0] >> 6) != 2) return false;  // версія має бути друга

    const bool     pad = (buf[0] >> 5) & 1;
    const bool     ext = (buf[0] >> 4) & 1;
    const unsigned cc  =  buf[0]       & 0x0F;

    h.marker = (buf[1] >> 7) & 1;
    h.pt     =  buf[1]       & 0x7F;
    h.seq    = rd16(buf + 2);
    h.ts     = rd32(buf + 4);
    h.ssrc   = rd32(buf + 8);

    size_t off = 12 + 4u * cc;             // за фіксованою частиною — список CSRC
    if (off > n) return false;

    if (ext) {                             // розширення заголовка, якщо піднято біт X
        if (off + 4 > n) return false;
        const size_t words = rd16(buf + off + 2);  // довжина — у 32-бітових словах,
        off += 4 + 4 * words;                      // самі чотири байти в неї не входять
        if (off > n) return false;
    }

    size_t end = n;
    if (pad) {                             // набивка живе в хвості
        if (end == off) return false;
        const size_t k = buf[end - 1];     // останній байт каже, скільки викинути (разом із собою)
        if (k == 0 || k > end - off) return false;
        end -= k;
    }

    h.payload     = buf + off;
    h.payload_len = end - off;
    return true;
}
