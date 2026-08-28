#include <cstring>

// PNG: 89 50 4E 47 0D 0A 1A 0A · JPEG: FF D8 FF · WebP: 'RIFF' <довжина> 'WEBP'
static bool looks_like_tile(const unsigned char* p, int n)
{
    if (!p || n < 16) return false;

    if (!std::memcmp(p, "\x89PNG\r\n\x1a\n", 8))                    // початок PNG
        return !std::memcmp(p + n - 8, "IEND\xae\x42\x60\x82", 8);  // і чанк IEND у кінці

    if (p[0] == 0xFF && p[1] == 0xD8 && p[2] == 0xFF)               // SOI + перший маркер
        return p[n - 2] == 0xFF && p[n - 1] == 0xD9;                // EOI

    if (!std::memcmp(p, "RIFF", 4) && !std::memcmp(p + 8, "WEBP", 4)) {
        const uint32_t sz = uint32_t(p[4])        | (uint32_t(p[5]) <<  8)
                          | (uint32_t(p[6]) << 16) | (uint32_t(p[7]) << 24);
        return int64_t(sz) + 8 == int64_t(n);     // оголошена довжина = фактична
    }
    return false;
}
