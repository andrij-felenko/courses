// Ідіоматичний розбір 24-бітних значень у C++
#include <span>
#include <cstdint>

struct RawAdcSamples {
    uint32_t pressure;
    uint32_t temperature;
};

[[nodiscard]] constexpr RawAdcSamples parse_raw_samples(std::span<const uint8_t, 6> buf) noexcept {
    const uint32_t raw_p = static_cast<uint32_t>(buf[0]) |
                          (static_cast<uint32_t>(buf[1]) << 8) |
                          (static_cast<uint32_t>(buf[2]) << 16);

    const uint32_t raw_t = static_cast<uint32_t>(buf[3]) |
                          (static_cast<uint32_t>(buf[4]) << 8) |
                          (static_cast<uint32_t>(buf[5]) << 16);

    return { raw_p, raw_t };
}
