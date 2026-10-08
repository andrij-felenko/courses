#include "ws2812b.hpp"

namespace embedded {

Color Color::fromHsv(uint8_t h, uint8_t s, uint8_t v) {
    if (s == 0) {
        return Color(v, v, v);
    }

    uint8_t region = h / 43;
    uint8_t remainder = (h - (region * 43)) * 6;

    uint8_t p = static_cast<uint8_t>((static_cast<uint16_t>(v) * (255 - s)) >> 8);
    uint8_t q = static_cast<uint8_t>((static_cast<uint16_t>(v) * (255 - ((static_cast<uint16_t>(s) * remainder) >> 8))) >> 8);
    uint8_t t = static_cast<uint8_t>((static_cast<uint16_t>(v) * (255 - ((static_cast<uint16_t>(s) * (255 - remainder)) >> 8))) >> 8);

    switch (region) {
        case 0:  return Color(v, t, p);
        case 1:  return Color(q, v, p);
        case 2:  return Color(p, v, t);
        case 3:  return Color(p, q, v);
        case 4:  return Color(t, p, v);
        default: return Color(v, p, q);
    }
}

Color Color::blend(Color c1, Color c2, uint8_t factor) {
    uint16_t f1 = 255 - factor;
    uint16_t f2 = factor;

    uint8_t r = static_cast<uint8_t>((c1.r * f1 + c2.r * f2) / 255);
    uint8_t g = static_cast<uint8_t>((c1.g * f1 + c2.g * f2) / 255);
    uint8_t b = static_cast<uint8_t>((c1.b * f1 + c2.b * f2) / 255);

    return Color(r, g, b);
}

} // namespace embedded
