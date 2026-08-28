#include <atomic>

std::atomic<uint32_t> ms_ticks{0};

extern "C" void TIM3_IRQHandler() {
    if (TIM3->SR & TIM_SR_UIF) {
        TIM3->SR = ~TIM_SR_UIF;
        ms_ticks.fetch_add(1, std::memory_order_relaxed);
    }
}
