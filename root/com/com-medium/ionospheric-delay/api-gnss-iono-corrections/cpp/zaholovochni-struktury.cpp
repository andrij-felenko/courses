#include <array>
#include <cstdint>
#include <cmath>
#include <optional>

namespace gnss::api {

/* Зпакована сира бітова структура кадру IS-GPS-200 */
struct alignas(1) GpsKlobucharRaw {
    std::int8_t alpha0_raw;
    std::int8_t alpha1_raw;
    std::int8_t alpha2_raw;
    std::int8_t alpha3_raw;
    std::int8_t beta0_raw;
    std::int8_t beta1_raw;
    std::int8_t beta2_raw;
    std::int8_t beta3_raw;
};

/* Ідіоматична структура C++ з вбудованою валидацією */
struct GpsKlobucharBroadcast {
    std::array<double, 4> alpha{};
    std::array<double, 4> beta{};
    std::uint32_t         tow_sec{0};
    bool                  valid{false};

    [[nodiscard]] static constexpr GpsKlobucharBroadcast decode(const GpsKlobucharRaw& raw, std::uint32_t tow) noexcept {
        GpsKlobucharBroadcast decoded{};
        decoded.alpha[0] = raw.alpha0_raw * std::pow(2.0, -30);
        decoded.alpha[1] = raw.alpha1_raw * std::pow(2.0, -27);
        decoded.alpha[2] = raw.alpha2_raw * std::pow(2.0, -24);
        decoded.alpha[3] = raw.alpha3_raw * std::pow(2.0, -24);

        decoded.beta[0]  = raw.beta0_raw  * std::pow(2.0, 11);
        decoded.beta[1]  = raw.beta1_raw  * std::pow(2.0, 14);
        decoded.beta[2]  = raw.beta2_raw  * std::pow(2.0, 16);
        decoded.beta[3]  = raw.beta3_raw  * std::pow(2.0, 16);

        decoded.tow_sec  = tow;
        decoded.valid    = decoded.checkBounds();
        return decoded;
    }

    [[nodiscard]] constexpr bool checkBounds() const noexcept {
        for (double a : alpha) {
            if (std::isnan(a)) return false;
        }
        for (double b : beta) {
            if (std::isnan(b)) return false;
        }
        return true;
    }
};

} // namespace gnss::api
