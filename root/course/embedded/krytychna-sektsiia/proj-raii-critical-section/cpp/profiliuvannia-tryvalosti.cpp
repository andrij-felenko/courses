#include "critical_section.hpp"
#include "core_cm4.h"
#include <concepts>

namespace embedded::debug {

class CriticalSectionProfiler {
public:
    static void init() noexcept {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }

    template <std::uint32_t MaxCycles, typename Callable>
    static void run_monitored(Callable&& action) noexcept {
        const std::uint32_t start_cycles = DWT->CYCCNT;
        
        {
            const sync::IrqGuard lock;
            action();
        }
        
        const std::uint32_t elapsed = DWT->CYCCNT - start_cycles;
        if (elapsed > MaxCycles) {
            __BKPT(0); // Зупинка зневаджувача при перевищенні ліміту
        }
    }
};

} // namespace embedded::debug
