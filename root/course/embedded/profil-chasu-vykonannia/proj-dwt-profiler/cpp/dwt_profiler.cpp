// dwt_profiler.cpp — пуск лічильника, калібрування й друк зведення.
#include "dwt_profiler.hpp"

#include <cstdio> // printf перенаправлено у власний _write() на UART

namespace embedded::profiler {

bool DwtProfiler::core_has_dwt() noexcept {
    // ARMv6-M (Cortex-M0/M0+) блоку DWT не має: за адресою 0xE0001000 або
    // нулі, або HardFault. Питаємо CPUID ДО першого дотику до DWT.
    // Поле ARCHITECTURE (біти 19:16): 0xC — ARMv6-M, 0xF — ARMv7-M/ARMv8-M.
    return ((mmio::reg(mmio::scb_cpuid) >> 16) & 0xFU) != 0xCU;
}

bool DwtProfiler::counter_runs() noexcept {
    if ((mmio::reg(mmio::dwt_ctrl) & mmio::dwt_cyccntena) == 0) {
        return false; // біт не втримався — лічильника тактів у DWT немає
    }

    // Біт може стояти, а лічильник не рухатися (урізаний DWT деяких чипів).
    const std::uint32_t probe = get_cycles();
    for (volatile int i = 0; i < 8; ++i) {
    }
    return get_cycles() != probe;
}

std::uint32_t DwtProfiler::calibrate() noexcept {
    // Мінімум серії, а не середнє: замір може лише подовшати — від
    // переривання, промаху кеша чи очікування Flash. Найкоротший результат
    // і є справжня ціна пари читань.
    std::uint32_t best = std::numeric_limits<std::uint32_t>::max();

    for (int i = 0; i < 32; ++i) {
        __asm__ volatile("" ::: "memory"); // бар'єр компілятора
        const std::uint32_t t0 = get_cycles();
        __asm__ volatile("" ::: "memory");
        const std::uint32_t t1 = get_cycles();

        if (const std::uint32_t delta = t1 - t0; delta < best) {
            best = delta;
        }
    }
    return best;
}

std::optional<std::uint32_t> DwtProfiler::init() noexcept {
    s_overhead = 0;

    if (!core_has_dwt()) {
        return std::nullopt;
    }

    mmio::reg(mmio::core_demcr) |= mmio::demcr_trcena; // без TRCENA DWT знеструмлений
    mmio::reg(mmio::dwt_lar) = mmio::lar_key;          // M7/M33: зняти замок запису
    mmio::reg(mmio::dwt_ctrl) |= mmio::dwt_cyccntena;
    mmio::reg(mmio::dwt_cyccnt) = 0;

    if (!counter_runs()) {
        return std::nullopt;
    }

    s_overhead = calibrate();
    return s_overhead;
}

void DwtProfiler::invalidate_icache() noexcept {
    if ((mmio::reg(mmio::scb_ccr) & mmio::ccr_icache) == 0) {
        return; // M3/M4: кеша інструкцій немає, інвалідувати нічого
    }
    __asm__ volatile("dsb 0xF" ::: "memory");
    mmio::reg(mmio::scb_iciallu) = 0;
    __asm__ volatile("dsb 0xF" ::: "memory");
    __asm__ volatile("isb 0xF" ::: "memory");
}

void report(std::string_view name, const ExecutionStats& stats, std::uint32_t cpu_freq_hz) {
    if (stats.samples == 0) {
        std::printf("%-14.*s замірів немає\n", static_cast<int>(name.size()), name.data());
        return;
    }

    const std::uint32_t avg = stats.average();
    const auto ns = [cpu_freq_hz](std::uint32_t cycles) {
        return static_cast<unsigned long>(DwtProfiler::to_nanoseconds(cycles, cpu_freq_hz));
    };

    std::printf("%-14.*s n=%lu  min=%lu т (%lu нс)  avg=%lu т (%lu нс)  max=%lu т (%lu нс)  джитер=%lu т\n",
                static_cast<int>(name.size()), name.data(),
                static_cast<unsigned long>(stats.samples),
                static_cast<unsigned long>(stats.min_cycles), ns(stats.min_cycles),
                static_cast<unsigned long>(avg), ns(avg),
                static_cast<unsigned long>(stats.max_cycles), ns(stats.max_cycles),
                static_cast<unsigned long>(stats.jitter()));
}

} // namespace embedded::profiler
