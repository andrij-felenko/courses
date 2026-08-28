#include <span>
#include <cstdint>

constexpr uint16_t CalculateKeyTag(std::span<const uint8_t> rdata, uint8_t algorithm) noexcept {
    if (algorithm == 1) { // RSAMD5 крайовий випадок
        if (rdata.size() < 3) return 0;
        return static_cast<uint16_t>((rdata[rdata.size() - 3] << 8) | rdata[rdata.size() - 2]);
    }

    uint32_t ac = 0;
    for (size_t i = 0; i < rdata.size(); ++i) {
        ac += (i & 1) ? rdata[i] : (static_cast<uint32_t>(rdata[i]) << 8);
    }
    ac += (ac >> 16) & 0xFFFF;
    return static_cast<uint16_t>(ac & 0xFFFF);
}
