// Бар'єри компілятора та ядра на C++20
#include <atomic>

inline uint32_t read_dwt_cycles_barrier() noexcept {
    std::atomic_signal_fence(std::memory_order_seq_cst);
    asm volatile("dsb 0xF" ::: "memory");
    asm volatile("isb 0xF" ::: "memory");
    const uint32_t val = *reinterpret_cast<volatile uint32_t*>(0xE0001004U);
    std::atomic_signal_fence(std::memory_order_seq_cst);
    return val;
}
