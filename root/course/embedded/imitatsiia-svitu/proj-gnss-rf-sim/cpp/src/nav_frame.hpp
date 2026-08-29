// nav_frame.hpp — навігаційне повідомлення 50 біт/с: п'ять підкадрів по 300 біт,
// зі справжньою парністю IS-GPS-200. Тут живуть номер тижня й секунда координації.
#pragma once

#include <array>
#include <cstdint>
#include <optional>

#include "ephemeris.hpp"
#include "gps_time.hpp"

namespace gnss {

inline constexpr double kNavBitRateHz = 50.0;

struct NavContext {
    std::array<double, 4>       alpha{}, beta{};    // коефіцієнти Клобучара в кадр
    LeapSecond                  leap{};
    std::array<std::uint8_t, 32> health{};          // стан сузір'я для альманаху
};

class NavFrame {
public:
    static constexpr std::size_t kBits = 1500;      // 5 підкадрів = 30 с
    static constexpr double      kDuration = 30.0;

    NavFrame(const Ephemeris& eph, const NavContext& ctx, GpsTime frame_start);

    // Номер біта для моменту випромінювання; порожньо — кадр застарів.
    [[nodiscard]] std::optional<double> bit_position(GpsTime t_tx) const noexcept;

    // Готовий знак ±1: множиться на чип коду без жодних перетворень.
    [[nodiscard]] std::int8_t sign_at(double position) const noexcept;

    [[nodiscard]] GpsTime start() const noexcept { return start_; }

private:
    std::array<std::int8_t, kBits> bits_{};
    GpsTime start_{};
};

}  // namespace gnss
