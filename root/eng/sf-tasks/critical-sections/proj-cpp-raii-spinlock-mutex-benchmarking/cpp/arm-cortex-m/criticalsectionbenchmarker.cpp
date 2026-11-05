#include <cstdint>
#include <atomic>
#include "stm32f4xx.h"

class CriticalSectionBenchmarker {
private:
    std::atomic_flag lock_flag = ATOMIC_FLAG_INIT;
    uint32_t min_cycles = 0xFFFFFFFFU;
    uint32_t max_cycles = 0;
    uint64_t total_cycles = 0;
    uint32_t sample_count = 0;

public:
    CriticalSectionBenchmarker() {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }

    template<typename Callable>
    void profile_scoped(Callable&& work) {
        uint32_t start = DWT->CYCCNT;
        {
            // Використання RAII обгортки з атомарним прапорцем
            while (lock_flag.test_and_set(std::memory_order_acquire)) {
                asm volatile("nop");
            }
            
            work();
            
            lock_flag.clear(std::memory_order_release);
        }
        uint32_t elapsed = DWT->CYCCNT - start;
        
        if (elapsed < min_cycles) min_cycles = elapsed;
        if (elapsed > max_cycles) max_cycles = elapsed;
        total_cycles += elapsed;
        sample_count++;
    }

    uint32_t get_average_cycles() const {
        return sample_count > 0 ? static_cast<uint32_t>(total_cycles / sample_count) : 0;
    }
};
