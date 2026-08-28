#include <cstdint>
#include <expected>
#include "stm32f4xx.h"

enum class DriverError : uint8_t {
    Timeout,
    BusLocked
};

inline void dwt_init() noexcept {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

[[nodiscard]] inline std::expected<void, DriverError> wait_flag_timeout(
    volatile const uint32_t& reg,
    uint32_t mask,
    bool wait_set,
    uint32_t timeout_us) noexcept 
{
    const uint32_t start_cycles = DWT->CYCCNT;
    const uint32_t max_cycles = timeout_us * (SystemCoreClock / 1000000U);

    while (true) {
        const bool condition = ((reg & mask) != 0);
        if (condition == wait_set) {
            return {};
        }
        if (static_cast<uint32_t>(DWT->CYCCNT - start_cycles) >= max_cycles) {
            return std::unexpected(DriverError::Timeout);
        }
    }
}
