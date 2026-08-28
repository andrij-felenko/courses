#include <array>
#include <cstdint>

namespace gnss::api {

struct SbasIgpPoint {
    std::uint16_t igp_id{0};
    double        delay_vertical_m{0.0};
    std::uint8_t  givei{15};
    double        sigma_give_m{1e9};
    bool          monitored{false};

    [[nodiscard]] static constexpr double decodeGiveiSigma(std::uint8_t givei) noexcept {
        constexpr std::array<double, 15> give_table{
            0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40,
            0.50, 0.60, 0.75, 1.00, 1.50, 2.50, 7.50
        };
        if (givei < 15) return give_table[givei];
        return 1e9; /* Поріг непридатності */
    }
};

struct SbasIgpCell {
    std::array<SbasIgpPoint, 4> corners{};

    [[nodiscard]] bool isValidForNavigation() const noexcept {
        for (const auto& pt : corners) {
            if (!pt.monitored || pt.givei >= 15) return false;
        }
        return true;
    }
};

} // namespace gnss::api
