#include <cstdint>

namespace McuAdc::Registers {

struct AdcCommonControl {
    static constexpr uint32_t vref_enable_pos   = 22U;
    static constexpr uint32_t vref_enable_mask  = (1UL << vref_enable_pos);

    static constexpr uint32_t temp_enable_pos   = 23U;
    static constexpr uint32_t temp_enable_mask  = (1UL << temp_enable_pos);

    static constexpr uint32_t vbat_enable_pos   = 24U;
    static constexpr uint32_t vbat_enable_mask  = (1UL << vbat_enable_pos);

    static constexpr uint32_t prescaler_pos     = 18U;
    static constexpr uint32_t prescaler_mask    = (0xFUL << prescaler_pos);
};

} // namespace McuAdc::Registers
