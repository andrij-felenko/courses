#include <cstdint>

namespace McuAdc {

enum class McuFamily {
    Stm32F4,
    Stm32G4,
    Stm32H7,
    Stm32U5
};

template <McuFamily Family>
struct FamilyTraits;

template <>
struct FamilyTraits<McuFamily::Stm32F4> {
    static constexpr uint8_t vbat_divider = 2U;
    static constexpr uint16_t cal_vref_mv = 3300U;
};

template <>
struct FamilyTraits<McuFamily::Stm32G4> {
    static constexpr uint8_t vbat_divider = 3U;
    static constexpr uint16_t cal_vref_mv = 3000U;
};

template <>
struct FamilyTraits<McuFamily::Stm32H7> {
    static constexpr uint8_t vbat_divider = 4U;
    static constexpr uint16_t cal_vref_mv = 3300U;
};

} // namespace McuAdc
