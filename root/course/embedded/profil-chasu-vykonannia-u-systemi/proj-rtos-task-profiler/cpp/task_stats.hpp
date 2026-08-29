// task_stats.hpp — дані профілювальника: знімок статистики, помилки, перерахунок тактів.
#pragma once

#include <chrono>
#include <cstdint>
#include <string_view>

namespace rt {

enum class ProfilerError {
    InvalidId,        // ідентифікатор поза межами масиву контрольних точок
    BadFrequency,     // нульова частота ядра
    HardwareMissing,  // CYCCNT не реалізовано або домен трасування спить
    NotStarted,       // профілювальник ще не пройшов start()
};

// Знімок агрегованої статистики однієї контрольної точки. Саме його віддає
// stats(): копія, зроблена під критичною секцією, а не посилання на живі дані.
struct TaskStats {
    std::string_view name{"-"};
    std::uint32_t expected_period_cyc{0}; // номінальний період; 0 — спорадична
    std::uint32_t min_cyc{UINT32_MAX};    // BCET
    std::uint32_t max_cyc{0};             // WCET
    std::uint64_t total_cyc{0};           // сума для ACET
    std::uint32_t call_count{0};
    std::uint32_t max_jitter_cyc{0};
    std::uint32_t last_start_cyc{0};
    std::uint32_t last_duration_cyc{0};
    std::uint32_t exc_cyc{0};             // такти переривань усередині вимірів
    std::uint32_t sleep_cyc{0};           // такти сну всередині вимірів
    std::uint32_t orphan_count{0};        // неспарені входи/виходи

    [[nodiscard]] constexpr std::uint32_t avg_cyc() const noexcept
    {
        return call_count == 0U ? 0U : static_cast<std::uint32_t>(total_cyc / call_count);
    }
};

// Перерахунок тактів у час і навпаки — цілочисельний, без плаваючої коми:
// на Cortex-M4F вона є, на M3 її немає, а звіт друкується однаково.
class CycleClock {
public:
    constexpr explicit CycleClock(std::uint32_t hz) noexcept : hz_{hz} {}

    [[nodiscard]] constexpr std::uint32_t hz() const noexcept { return hz_; }

    [[nodiscard]] constexpr std::chrono::microseconds to_us(std::uint32_t cyc) const noexcept
    {
        return std::chrono::microseconds{static_cast<std::int64_t>(
            static_cast<std::uint64_t>(cyc) * 1'000'000ULL / hz_)};
    }

    [[nodiscard]] constexpr std::chrono::nanoseconds to_ns(std::uint32_t cyc) const noexcept
    {
        return std::chrono::nanoseconds{static_cast<std::int64_t>(
            static_cast<std::uint64_t>(cyc) * 1'000'000'000ULL / hz_)};
    }

    [[nodiscard]] constexpr std::uint32_t from(std::chrono::microseconds us) const noexcept
    {
        const auto ticks = static_cast<std::uint64_t>(us.count() < 0 ? 0 : us.count());
        return static_cast<std::uint32_t>(ticks * hz_ / 1'000'000ULL);
    }

private:
    std::uint32_t hz_;
};

} // namespace rt
