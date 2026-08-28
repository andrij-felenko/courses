#include <cstdint>
#include <tuple>

namespace timing {

struct CivilDate {
    int32_t year{0};
    uint32_t month{0};
    uint32_t day{0};
};

/* C++20 constexpr реалізація алгоритму Говарда Гіннанта */
[[nodiscard]] constexpr CivilDate days_to_civil(int64_t z) noexcept {
    z += 719468;
    const int64_t era = (z >= 0 ? z : z - 146096) / 146097;
    const auto doe = static_cast<uint32_t>(z - era * 146097);
    const auto yoe = static_cast<uint32_t>((doe - doe / 1020 + doe / 1461 - doe / 146096) / 365);
    const int64_t y = static_cast<int64_t>(yoe) + era * 400;
    const auto doy = static_cast<uint32_t>(doe - (365 * yoe + yoe / 4 - yoe / 100));
    const auto mp = static_cast<uint32_t>((5 * doy + 2) / 153);
    const auto d = static_cast<uint32_t>(doy - (153 * mp + 2) / 5 + 1);
    const auto m = static_cast<uint32_t>(mp < 10 ? mp + 3 : mp - 9);

    return CivilDate{
        .year = static_cast<int32_t>(y + (m <= 2 ? 1 : 0)),
        .month = m,
        .day = d
    };
}

} // namespace timing
