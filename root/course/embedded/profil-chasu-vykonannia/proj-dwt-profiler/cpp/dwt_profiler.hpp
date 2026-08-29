// dwt_profiler.hpp — профілювання ділянок коду лічильником DWT->CYCCNT (C++20).
//
// Ядра ARMv7-M (Cortex-M3/M4/M7) і ARMv8-M (M33). На ARMv6-M (M0/M0+) блоку
// DWT немає: init() поверне порожній optional, і рахувати треба SysTickCounter.
#pragma once

#include <concepts>
#include <cstdint>
#include <limits>
#include <optional>
#include <string_view>
#include <type_traits>
#include <utility>

namespace embedded::profiler {

// Доступ до регістрів налагодження. Адреси однакові для всіх Cortex-M
// зазначених архітектур, тож CMSIS-заголовок чипа тут не потрібен.
namespace mmio {

[[nodiscard]] inline volatile std::uint32_t& reg(std::uintptr_t address) noexcept {
    return *reinterpret_cast<volatile std::uint32_t*>(address);
}

inline constexpr std::uintptr_t scb_cpuid = 0xE000ED00U;
inline constexpr std::uintptr_t scb_ccr = 0xE000ED14U;
inline constexpr std::uintptr_t scb_iciallu = 0xE000EF50U;
inline constexpr std::uintptr_t core_demcr = 0xE000EDFCU;
inline constexpr std::uintptr_t dwt_ctrl = 0xE0001000U;
inline constexpr std::uintptr_t dwt_cyccnt = 0xE0001004U;
inline constexpr std::uintptr_t dwt_lar = 0xE0001FB0U;

inline constexpr std::uint32_t demcr_trcena = 1U << 24;
inline constexpr std::uint32_t dwt_cyccntena = 1U << 0;
inline constexpr std::uint32_t lar_key = 0xC5ACCE55U;
inline constexpr std::uint32_t ccr_icache = 1U << 17;

} // namespace mmio

/// Накопичений розкид замірів однієї ділянки.
struct ExecutionStats {
    std::uint32_t min_cycles{std::numeric_limits<std::uint32_t>::max()};
    std::uint32_t max_cycles{0};
    std::uint64_t total_cycles{0};
    std::uint32_t samples{0};

    constexpr void update(std::uint32_t cycles) noexcept {
        if (samples == 0) {
            min_cycles = cycles;
            max_cycles = cycles;
        } else {
            if (cycles < min_cycles) {
                min_cycles = cycles;
            }
            if (cycles > max_cycles) {
                max_cycles = cycles;
            }
        }
        total_cycles += cycles;
        ++samples;
    }

    [[nodiscard]] constexpr std::uint32_t average() const noexcept {
        return samples > 0 ? static_cast<std::uint32_t>(total_cycles / samples) : 0U;
    }

    /// Джитер — розкид між найгіршим і найкращим прогоном.
    [[nodiscard]] constexpr std::uint32_t jitter() const noexcept {
        return samples > 0 ? max_cycles - min_cycles : 0U;
    }

    constexpr void reset() noexcept { *this = ExecutionStats{}; }
};

class DwtProfiler {
public:
    /// Вмикає лічильник і калібрує накладні витрати.
    /// @return накладні витрати в тактах або порожньо, якщо DWT недоступний.
    static std::optional<std::uint32_t> init() noexcept;

    [[nodiscard]] static std::uint32_t get_cycles() noexcept {
        return mmio::reg(mmio::dwt_cyccnt);
    }

    [[nodiscard]] static std::uint32_t elapsed_cycles(std::uint32_t start_cycles) noexcept {
        const std::uint32_t now = get_cycles();
        // Беззнакове віднімання за модулем 2^32 правильне й тоді, коли
        // лічильник під час заміру перейшов через 0xFFFFFFFF.
        const std::uint32_t raw = now - start_cycles;
        return raw > s_overhead ? raw - s_overhead : 0U;
    }

    [[nodiscard]] static constexpr std::uint64_t to_nanoseconds(std::uint32_t cycles,
                                                                std::uint32_t cpu_freq_hz) noexcept {
        if (cpu_freq_hz == 0) {
            return 0U;
        }
        const std::uint64_t scaled =
            static_cast<std::uint64_t>(cycles) * 1'000'000'000ULL + cpu_freq_hz / 2U;
        return scaled / cpu_freq_hz;
    }

    [[nodiscard]] static std::uint32_t overhead() noexcept { return s_overhead; }

    /// Викидає кеш інструкцій — «холодний старт» для заміру WCET.
    static void invalidate_icache() noexcept;

private:
    static bool core_has_dwt() noexcept;
    static bool counter_runs() noexcept;
    static std::uint32_t calibrate() noexcept;

    static inline std::uint32_t s_overhead{0};
};

/// RAII-замір: статистика оновлюється в деструкторі, тож ранній return
/// чи виняток не губить прогону.
class ScopedTimer {
public:
    explicit ScopedTimer(ExecutionStats& stats) noexcept
        : m_stats{stats}, m_start{DwtProfiler::get_cycles()} {}

    ~ScopedTimer() noexcept { m_stats.update(DwtProfiler::elapsed_cycles(m_start)); }

    ScopedTimer(const ScopedTimer&) = delete;
    ScopedTimer& operator=(const ScopedTimer&) = delete;
    ScopedTimer(ScopedTimer&&) = delete;
    ScopedTimer& operator=(ScopedTimer&&) = delete;

private:
    ExecutionStats& m_stats;
    std::uint32_t m_start;
};

/// Одноразовий замір довільного виклику: повертає такти, нічого не накопичуючи.
template <std::invocable Body>
[[nodiscard]] std::uint32_t measure(Body&& body) noexcept(std::is_nothrow_invocable_v<Body>) {
    const std::uint32_t start = DwtProfiler::get_cycles();
    std::forward<Body>(body)();
    return DwtProfiler::elapsed_cycles(start);
}

/// Друк зведення по накопиченій статистиці.
void report(std::string_view name, const ExecutionStats& stats, std::uint32_t cpu_freq_hz);

} // namespace embedded::profiler
