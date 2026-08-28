#include <stdint.h>
#include <stdbool.h>

/* Перетворення BCD в десятковий двійковий формат */
static inline uint8_t rtc_bcd2bin(uint8_t val) {
    return (uint8_t)(((val >> 4) * 10) + (val & 0x0F));
}

/* Перетворення двійкового формату в BCD */
static inline uint8_t rtc_bin2bcd(uint8_t val) {
    return (uint8_t)(((val / 10) << 4) | (val % 10));
}

/* Перевірка правила високосного року за григоріанським календарем */
static inline bool rtc_is_leap_year(uint16_t year) {
    return ((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0);
}

/* Таблиця кумулятивної кількості днів перед початком кожного місяця */
static const uint16_t days_before_month_table[13] = {
    0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334
};

/* Розрахунок 64-бітної мітки часу UNIX Epoch у мікросекундах */
uint64_t rtc_to_unix_epoch_us(uint16_t year, uint8_t month, uint8_t day,
                              uint8_t hours, uint8_t minutes, uint8_t seconds,
                              uint32_t ssr_raw, uint32_t prediv_s) {
    if (year < 1970 || month < 1 || month > 12 || day < 1 || day > 31) return 0;

    /* Розрахунок кількості повних днів від 1 січня 1970 року */
    uint32_t days = 0;
    for (uint16_t y = 1970; y < year; y++) {
        days += rtc_is_leap_year(y) ? 366 : 365;
    }
    days += days_before_month_table[month];
    if (month > 2 && rtc_is_leap_year(year)) {
        days += 1;
    }
    days += (day - 1);

    uint64_t total_sec = ((uint64_t)days * 86400ULL) +
                         ((uint64_t)hours * 3600ULL) +
                         ((uint64_t)minutes * 60ULL) +
                         (uint64_t)seconds;

    /* Субсекундна інтерполяція через зворотний лічильник SSR */
    uint64_t subsecond_us = 0;
    if (prediv_s > 0) {
        if (ssr_raw > prediv_s) ssr_raw = prediv_s;
        uint64_t elapsed_ticks = (uint64_t)(prediv_s - ssr_raw);
        subsecond_us = (elapsed_ticks * 1000000ULL) / (uint64_t)(prediv_s + 1);
    }

    return (total_sec * 1000000ULL) + subsecond_us;
}
