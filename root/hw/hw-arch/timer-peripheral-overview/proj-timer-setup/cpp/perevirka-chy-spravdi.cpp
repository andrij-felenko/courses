#include <chrono>

namespace hal::timer {

uint32_t tim_clk_hz() {
    const uint32_t ppre1 = (RCC->CFGR & RCC_CFGR_PPRE1) >> RCC_CFGR_PPRE1_Pos;
    const uint32_t pclk1 = SystemCoreClock >> APBPrescTable[ppre1];
    return (ppre1 < 4u) ? pclk1 : pclk1 * 2u;
}

std::chrono::nanoseconds tim3_period() {
    const uint64_t ticks = static_cast<uint64_t>(TIM3->PSC + 1u) * (TIM3->ARR + 1u);
    const uint64_t ns = (ticks * 1'000'000'000ULL) / tim_clk_hz();
    return std::chrono::nanoseconds(ns);
}

} // namespace hal::timer
