#include <cstdint>
#include <chrono>
#include <expected>
#include <array>
#include <cmath>

namespace rtc {

using namespace std::chrono_literals;

/* Типізована структура календарного часу */
struct DateTime {
    uint16_t year{2026};        // 1970..2099
    uint8_t  month{1};          // 1..12
    uint8_t  day{1};            // 1..31
    uint8_t  hours{0};          // 0..23
    uint8_t  minutes{0};        // 0..59
    uint8_t  seconds{0};        // 0..59
    uint32_t subsecond_us{0};   // 0..999999

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        if (year < 1970 || month < 1 || month > 12 || day < 1 || day > 31) return false;
        if (hours > 23 || minutes > 59 || seconds > 59 || subsecond_us >= 1'000'000) return false;
        return true;
    }
};

/* Параметри цифрового згладжувального калібрування */
struct CalibrationParams {
    bool     calp{false};       // true = вставка +512 тактів
    uint16_t calm{0};           // маскування 0..511 тактів
    float    residual_ppm{0.0f};// залишкова похибка
};

enum class CalibrationError {
    OutOfRange,
    InvalidInput
};

/* Функції перетворення BCD */
[[nodiscard]] constexpr uint8_t bcd_to_bin(uint8_t bcd) noexcept {
    return static_cast<uint8_t>(((bcd >> 4) * 10) + (bcd & 0x0F));
}

[[nodiscard]] constexpr uint8_t bin_to_bcd(uint8_t bin) noexcept {
    return static_cast<uint8_t>(((bin / 10) << 4) | (bin % 10));
}

[[nodiscard]] constexpr bool is_leap_year(uint16_t year) noexcept {
    return ((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0);
}

constexpr std::array<uint16_t, 13> days_before_month = {
    0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334
};

/* Розрахунок субсекундної частки в мікросекундах */
[[nodiscard]] constexpr uint32_t calculate_subsecond_us(uint32_t ssr_raw, uint32_t prediv_s) noexcept {
    if (prediv_s == 0) return 0;
    if (ssr_raw > prediv_s) ssr_raw = prediv_s;
    const uint64_t elapsed_ticks = prediv_s - ssr_raw;
    return static_cast<uint32_t>((elapsed_ticks * 1'000'000ULL) / (prediv_s + 1));
}

/* Розрахунок параметрів плавного калібрування */
[[nodiscard]] constexpr std::expected<CalibrationParams, CalibrationError>
calculate_smooth_calibration(float measured_ppm) noexcept {
    constexpr float STEP_PPM = 0.953674316f;
    constexpr float CALP_PPM = 488.28125f;

    if (measured_ppm > 487.32f || measured_ppm < -488.28f) {
        return std::unexpected(CalibrationError::OutOfRange);
    }

    CalibrationParams params{};
    if (measured_ppm >= 0.0f) {
        params.calp = false;
        auto calm_val = static_cast<int32_t>((measured_ppm / STEP_PPM) + 0.5f);
        if (calm_val > 511) calm_val = 511;
        params.calm = static_cast<uint16_t>(calm_val);
        params.residual_ppm = measured_ppm - (static_cast<float>(calm_val) * STEP_PPM);
    } else {
        params.calp = true;
        float target_reduction = CALP_PPM - (-measured_ppm);
        auto calm_val = static_cast<int32_t>((target_reduction / STEP_PPM) + 0.5f);
        if (calm_val < 0) calm_val = 0;
        if (calm_val > 511) calm_val = 511;
        params.calm = static_cast<uint16_t>(calm_val);
        params.residual_ppm = measured_ppm - (CALP_PPM - (static_cast<float>(calm_val) * STEP_PPM));
    }

    return params;
}

/* Конвертація DateTime у std::chrono::microseconds (UNIX epoch) */
[[nodiscard]] constexpr std::chrono::microseconds to_unix_epoch(const DateTime& dt) noexcept {
    if (!dt.is_valid()) return 0us;

    uint32_t days = 0;
    for (uint16_t y = 1970; y < dt.year; ++y) {
        days += is_leap_year(y) ? 366 : 365;
    }

    days += days_before_month[dt.month];
    if (dt.month > 2 && is_leap_year(dt.year)) {
        days += 1;
    }
    days += (dt.day - 1);

    auto total_sec = std::chrono::seconds(
        (static_cast<uint64_t>(days) * 86400ULL) +
        (static_cast<uint64_t>(dt.hours) * 3600ULL) +
        (static_cast<uint64_t>(dt.minutes) * 60ULL) +
        static_cast<uint64_t>(dt.seconds)
    );

    return std::chrono::duration_cast<std::chrono::microseconds>(total_sec) +
           std::chrono::microseconds(dt.subsecond_us);
}

/* Безпечний диспетчер подвійного часу (Монотонний + Календарний) */
class DualTimeManager {
public:
    constexpr DualTimeManager(std::chrono::microseconds initial_wall,
                              std::chrono::microseconds initial_hw_ticks) noexcept
        : last_monotonic_(initial_hw_ticks),
          wall_offset_(initial_wall - initial_hw_ticks) {}

    /* Отримання гарантовано монотонного часу (ніколи не повертається назад) */
    [[nodiscard]] std::chrono::microseconds get_monotonic(std::chrono::microseconds raw_hw_ticks) noexcept {
        if (raw_hw_ticks > last_monotonic_) {
            last_monotonic_ = raw_hw_ticks;
        }
        return last_monotonic_;
    }

    /* Отримання календарного часу */
    [[nodiscard]] std::chrono::microseconds get_wall_time(std::chrono::microseconds raw_hw_ticks) noexcept {
        const auto mono = get_monotonic(raw_hw_ticks);
        const auto wall = mono + wall_offset_;
        return wall.count() > 0 ? wall : 0us;
    }

    /* Оновлення часу від NTP без збоїв інтервального вимірювання */
    void synchronize_ntp(std::chrono::microseconds raw_hw_ticks,
                         std::chrono::microseconds ntp_wall) noexcept {
        const auto mono = get_monotonic(raw_hw_ticks);
        wall_offset_ = ntp_wall - mono;
    }

private:
    std::chrono::microseconds last_monotonic_{0us};
    std::chrono::microseconds wall_offset_{0us};
};

} // namespace rtc
