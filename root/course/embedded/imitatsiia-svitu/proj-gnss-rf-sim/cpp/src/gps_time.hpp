// gps_time.hpp — шкала часу GPS: повний лічильник тижнів, той, що їде в кадр,
// і секунда координації.
#pragma once

#include <cmath>

namespace gnss {

inline constexpr double kSecondsPerWeek = 604800.0;

class GpsTime {
public:
    constexpr GpsTime() = default;
    constexpr GpsTime(int week, double tow) : week_{week}, tow_{tow} { normalize(); }

    [[nodiscard]] constexpr int    week() const noexcept { return week_; }
    [[nodiscard]] constexpr double tow()  const noexcept { return tow_; }

    // У навігаційне повідомлення йдуть лише молодші 10 біт — раз на 1024 тижні
    // лічильник переповнюється, і саме це перевіряє стенд.
    [[nodiscard]] constexpr int broadcast_week() const noexcept { return week_ & 0x3FF; }

    constexpr GpsTime& operator+=(double dt) noexcept { tow_ += dt; normalize(); return *this; }

    [[nodiscard]] friend constexpr GpsTime operator+(GpsTime t, double dt) noexcept {
        return t += dt;
    }
    [[nodiscard]] friend constexpr double operator-(const GpsTime& a, const GpsTime& b) noexcept {
        return static_cast<double>(a.week_ - b.week_) * kSecondsPerWeek + (a.tow_ - b.tow_);
    }

    // Кадр починається лише на межі 30 с — інакше приймач не зловить преамбулу.
    [[nodiscard]] GpsTime aligned_to(double step) const noexcept {
        return {week_, std::floor(tow_ / step) * step};
    }

private:
    constexpr void normalize() noexcept {
        while (tow_ >= kSecondsPerWeek) { tow_ -= kSecondsPerWeek; ++week_; }
        while (tow_ < 0.0)              { tow_ += kSecondsPerWeek; --week_; }
    }

    int    week_{};
    double tow_{};
};

struct LeapSecond {
    int current{18};   // ΔtLS
    int future{18};    // ΔtLSF після стрибка
    int wn_lsf{};      // тиждень уведення, 8 біт
    int dn{1};         // день тижня
};

}  // namespace gnss
