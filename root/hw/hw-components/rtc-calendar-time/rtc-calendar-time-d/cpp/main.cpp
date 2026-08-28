#include <cstdint>
#include <chrono>
#include <array>

namespace rtc {

using namespace std::chrono_literals;

/* Перетворення BCD у двійковий формат під час компіляції */
[[nodiscard]] constexpr uint8_t bcd_to_bin(uint8_t val) noexcept {
    return static_cast<uint8_t>(((val >> 4) * 10) + (val & 0x0F));
}

/* Перетворення двійкового формату у BCD */
[[nodiscard]] constexpr uint8_t bin_to_bcd(uint8_t val) noexcept {
    return static_cast<uint8_t>(((val / 10) << 4) | (val % 10));
}

/* Перевірка високосного року */
[[nodiscard]] constexpr bool is_leap_year(uint16_t year) noexcept {
    return ((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0);
}

constexpr std::array<uint16_t, 13> days_before_month_table = {
    0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334
};

/* Розрахунок типізованої тривалості UNIX Epoch із субсекундною точністю */
[[nodiscard]] constexpr std::chrono::microseconds to_unix_epoch(
    uint16_t year, uint8_t month, uint8_t day,
    uint8_t hours, uint8_t minutes, uint8_t seconds,
    uint32_t ssr_raw, uint32_t prediv_s) noexcept {

    if (year < 1970 || month < 1 || month > 12 || day < 1 || day > 31) return 0us;

    uint32_t days = 0;
    for (uint16_t y = 1970; y < year; ++y) {
        days += is_leap_year(y) ? 366 : 365;
    }
    days += days_before_month_table[month];
    if (month > 2 && is_leap_year(year)) {
        days += 1;
    }
    days += (day - 1);

    auto total_sec = std::chrono::seconds(
        (static_cast<uint64_t>(days) * 86400ULL) +
        (static_cast<uint64_t>(hours) * 3600ULL) +
        (static_cast<uint64_t>(minutes) * 60ULL) +
        static_cast<uint64_t>(seconds)
    );

    uint64_t subsecond_us = 0;
    if (prediv_s > 0) {
        if (ssr_raw > prediv_s) ssr_raw = prediv_s;
        const uint64_t elapsed_ticks = prediv_s - ssr_raw;
        subsecond_us = (elapsed_ticks * 1'000'000ULL) / (prediv_s + 1);
    }

    return std::chrono::duration_cast<std::chrono::microseconds>(total_sec) +
           std::chrono::microseconds(subsecond_us);
}

} // namespace rtc
