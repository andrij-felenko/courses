#include <array>
#include <cstdint>
#include <algorithm>

struct CvbsColorEntry {
    std::array<std::uint8_t, 4> dacSamples{};

    template <typename Func>
    static constexpr CvbsColorEntry fromRgb(std::uint8_t r, std::uint8_t g, std::uint8_t b,
                                           Func&& ireToDacFn) noexcept {
        CvbsColorEntry entry{};
        const float yIre = 0.299f * r + 0.587f * g + 0.114f * b;
        const float uIre = 0.492f * (b - yIre);
        const float vIre = 0.877f * (r - yIre);

        const float c0 =  vIre;
        const float c1 =  uIre;
        const float c2 = -vIre;
        const float c3 = -uIre;

        entry.dacSamples[0] = ireToDacFn(static_cast<std::int16_t>(yIre + c0));
        entry.dacSamples[1] = ireToDacFn(static_cast<std::int16_t>(yIre + c1));
        entry.dacSamples[2] = ireToDacFn(static_cast<std::int16_t>(yIre + c2));
        entry.dacSamples[3] = ireToDacFn(static_cast<std::int16_t>(yIre + c3));
        return entry;
    }
};
