#include <cstdint>
#include <span>

namespace mcu::power {

/* Базові адреси периферійних вузлів */
inline constexpr std::uintptr_t OPAMP_REG = 0x40007800UL;
inline constexpr std::uintptr_t COMP_REG  = 0x40010200UL;
inline constexpr std::uintptr_t DAC_REG   = 0x40007400UL;
inline constexpr std::uintptr_t TIM1_REG  = 0x40012C00UL;

/* Системний драйвер апаратного захисту */
class HardwareProtection final {
private:
    struct OpAmpRegs { volatile std::uint32_t CSR; };
    struct CompRegs  { volatile std::uint32_t CSR; };
    struct DacRegs   { volatile std::uint32_t CR; volatile std::uint32_t SWTRIGR; volatile std::uint32_t DHR12R1; };
    struct TimRegs   { volatile std::uint32_t CR1; volatile std::uint32_t RESERVED[17]; volatile std::uint32_t BDTR; };

public:
    HardwareProtection() = delete;

    static void initProtectionLoop(std::uint16_t dacCodeThreshold) noexcept {
        auto& dac   = *reinterpret_cast<DacRegs*>(DAC_REG);
        auto& opamp = *reinterpret_cast<OpAmpRegs*>(OPAMP_REG);
        auto& comp  = *reinterpret_cast<CompRegs*>(COMP_REG);
        auto& tim1  = *reinterpret_cast<TimRegs*>(TIM1_REG);

        // 1. Встановлення опорного порогу ЦАП
        dac.DHR12R1 = dacCodeThreshold & 0xFFFUL;
        dac.CR |= (1UL << 0); // Ввімкнути ЦАП

        // 2. Ввімкнення ОП у режимі PGA 16x з внутрішнім виходом
        constexpr std::uint32_t OPAMP_PGA_16X = (1UL << 30) | (0x3UL << 14) | (0x2UL << 5) | (1UL << 0);
        opamp.CSR = OPAMP_PGA_16X;

        // 3. Компаратор: вхід від OPAMP, поріг від DAC, гістерезис 20 мВ
        constexpr std::uint32_t COMP_CONFIG = (0x2UL << 16) | (0x1UL << 7) | (0x4UL << 4) | (1UL << 0);
        comp.CSR = COMP_CONFIG;
        comp.CSR |= (1UL << 31); // Апаратний LOCK регістра до системного Reset

        // 4. Увімкнення Break-захисту в таймері ШІМ
        constexpr std::uint32_t TIM_BREAK_ENABLE = (1UL << 12) | (1UL << 15);
        tim1.BDTR |= TIM_BREAK_ENABLE;
    }
};

} // namespace mcu::power
