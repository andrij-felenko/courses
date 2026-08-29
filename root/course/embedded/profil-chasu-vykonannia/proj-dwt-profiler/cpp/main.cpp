// main.cpp — демонстрація: ACET із прогрівом, WCET із холодним кешем,
// тривалість обробника переривання й запасний шлях через SysTick.
#include "dwt_profiler.hpp"
#include "gpio_strobe.hpp"
#include "systick_counter.hpp"

#include <array>
#include <cstdio>
#include <span>

namespace {

using namespace embedded::profiler;

constexpr std::uint32_t cpu_freq_hz = 216'000'000U; // такт ≈ 4.63 нс
constexpr std::size_t frame_len = 64;

using Strobe = StrobePin<gpio::port_b, 5>;

constexpr std::array<float, 8> taps{0.02f, 0.06f, 0.12f, 0.20f, 0.20f, 0.12f, 0.06f, 0.02f};

std::array<float, frame_len> g_frame{};
ExecutionStats g_isr_stats;
bool g_use_systick = false; // ядро без DWT — міряємо SysTick

// noinline обов'язковий: вбудована в цикл заміру функція розчиняється в ньому,
// і лічильник покаже час чогось іншого.
[[gnu::noinline]] void fir_filter(std::span<float> frame) noexcept {
    for (std::size_t i = taps.size() - 1; i < frame.size(); ++i) {
        float acc = 0.0f;
        for (std::size_t k = 0; k < taps.size(); ++k) {
            acc += taps[k] * frame[i - k];
        }
        frame[i] = acc;
    }
}

void fill_frame() noexcept {
    for (std::size_t i = 0; i < g_frame.size(); ++i) {
        g_frame[i] = static_cast<float>(i % 16) * 0.125f;
    }
}

[[nodiscard]] std::uint32_t bench_start() noexcept {
    return g_use_systick ? SysTickCounter::start() : DwtProfiler::get_cycles();
}

[[nodiscard]] std::uint32_t bench_elapsed(std::uint32_t start) noexcept {
    return g_use_systick ? SysTickCounter::elapsed_cycles(start)
                         : DwtProfiler::elapsed_cycles(start);
}

// ACET: перший прогін іде з Flash у порожній кеш і завжди довший за решту.
// Прогріваємо й відкидаємо його — інакше він сам стає «максимумом».
[[nodiscard]] ExecutionStats measure_acet(unsigned runs) noexcept {
    ExecutionStats stats;

    fill_frame();
    fir_filter(g_frame); // прогрів, у статистику не йде

    for (unsigned i = 0; i < runs; ++i) {
        fill_frame();
        const std::uint32_t start = bench_start();
        fir_filter(g_frame);
        stats.update(bench_elapsed(start));
    }
    return stats;
}

// WCET: перед кожним прогоном викидаємо кеш інструкцій — так виглядає
// обробник, чий код витіснили інші задачі. Саме це число йде в бюджет.
[[nodiscard]] ExecutionStats measure_wcet(unsigned runs) noexcept {
    ExecutionStats stats;

    for (unsigned i = 0; i < runs; ++i) {
        fill_frame();
        DwtProfiler::invalidate_icache();
        const std::uint32_t start = bench_start();
        fir_filter(g_frame);
        stats.update(bench_elapsed(start));
    }
    return stats;
}

} // namespace

// Обробник зовнішнього переривання: осцилограф бачить ширину імпульсу,
// а DWT рахує ту саму ділянку в тактах — два незалежні свідки одного числа.
extern "C" void EXTI0_IRQHandler() {
    ScopedStrobe<Strobe> strobe;
    ScopedTimer timer{g_isr_stats};

    // Прапорець гасимо на початку: лишений наприкінці, він забирає з собою
    // подію, що прийшла під час обробки.
    constexpr std::uintptr_t exti_pr = 0x40013C14U;
    mmio::reg(exti_pr) = 1U << 0;

    fir_filter(g_frame);
}

int main() {
    if (const auto overhead = DwtProfiler::init(); overhead.has_value()) {
        std::printf("DWT: накладні витрати %lu тактів\n",
                    static_cast<unsigned long>(*overhead));
    } else {
        // Cortex-M0/M0+ або чип з урізаним DWT — переходимо на SysTick.
        g_use_systick = true;
        std::printf("DWT недоступний, міряємо SysTick: накладні витрати %lu тактів\n",
                    static_cast<unsigned long>(SysTickCounter::init()));
    }

    Strobe::configure();

    const ExecutionStats acet = measure_acet(200);
    const ExecutionStats wcet = measure_wcet(50);

    report("FIR ACET", acet, cpu_freq_hz);
    report("FIR WCET", wcet, cpu_freq_hz);

    // Одноразовий замір без накопичення — для швидкої перевірки на місці.
    const std::uint32_t single = measure([] { fir_filter(g_frame); });
    std::printf("FIR один прогін: %lu тактів (%lu нс)\n",
                static_cast<unsigned long>(single),
                static_cast<unsigned long>(DwtProfiler::to_nanoseconds(single, cpu_freq_hz)));

    for (;;) {
        // Статистику обробника наповнює EXTI0_IRQHandler.
        if (g_isr_stats.samples >= 100) {
            report("EXTI0 ISR", g_isr_stats, cpu_freq_hz);
            g_isr_stats.reset();
        }
    }
}
