#include <cstdint>
#include <atomic>

// На C++ для контролю доступу використовують апаратні бар'єри CMSIS або std::atomic_thread_fence
extern "C" void __DMB(void);

struct DMAChannel {
    volatile std::uint32_t CCR;
    volatile std::uint32_t CNDTR;
    volatile std::uint32_t CPAR;
    volatile std::uint32_t CMAR;
};

void trigger_dma_safe(DMAChannel &dma) {
    // Встановлення апаратного бар'єра пам'яті
    __DMB();
    dma.CCR |= 0x01U; // Запуск DMA
}
