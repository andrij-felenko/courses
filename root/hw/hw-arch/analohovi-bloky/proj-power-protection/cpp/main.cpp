#include <cstdint>
#include <concepts>
#include <span>

namespace hw::analog {

/* Базові адреси периферійних модулів */
inline constexpr std::uintptr_t OPAMP_BASE = 0x40007800UL;
inline constexpr std::uintptr_t COMP_BASE  = 0x40010200UL;
inline constexpr std::uintptr_t DAC1_BASE  = 0x40007400UL;
inline constexpr std::uintptr_t TIM1_BASE  = 0x40012C00UL;
inline constexpr std::uintptr_t ADC1_BASE  = 0x50000000UL;

/* Режими коефіцієнта підсилення PGA */
enum class PgaGain : std::uint32_t {
    Gain2x  = 0x0UL << 14,
    Gain4x  = 0x1UL << 14,
    Gain8x  = 0x2UL << 14,
    Gain16x = 0x3UL << 14,
    Gain32x = 0x4UL << 14,
    Gain64x = 0x5UL << 14
};

/* Рівні гістерезису компаратора */
enum class Hysteresis : std::uint32_t {
    None   = 0x0UL << 16,
    Low    = 0x1UL << 16, // ~10 мВ
    Medium = 0x2UL << 16, // ~20 мВ
    High   = 0x3UL << 16  // ~40 мВ
};

/* Драйвер вбудованого операційного підсилювача */
class OpAmpPga {
private:
    struct Registers {
        volatile std::uint32_t CSR;
        volatile std::uint32_t RESERVED[5];
        volatile std::uint32_t OTR;
    };

    static Registers& regs() noexcept {
        return *reinterpret_cast<Registers*>(OPAMP_BASE);
    }

public:
    static void calibrate() noexcept {
        regs().CSR |= (1UL << 11); // CALON

        // Пошук зсуву диференціальної пари
        for (std::uint32_t i = 0; i < 32; ++i) {
            regs().OTR = (regs().OTR & ~0x1FUL) | (i & 0x1FUL);
            for (volatile int d = 0; d < 200; ++d);
            if (regs().CSR & (1UL << 12)) break;
        }

        regs().CSR &= ~(1UL << 11); // Вимкнення калібрування
    }

    static void init(PgaGain gain) noexcept {
        calibrate();

        constexpr std::uint32_t OPAMPINTEN  = (1UL << 30);
        constexpr std::uint32_t VM_SEL_PGA  = (0x2UL << 5);
        constexpr std::uint32_t VP_SEL_INP0 = (0x0UL << 2);
        constexpr std::uint32_t OPAMP_EN    = (1UL << 0);

        regs().CSR = OPAMPINTEN | static_cast<std::uint32_t>(gain) |
                     VM_SEL_PGA | VP_SEL_INP0 | OPAMP_EN;
    }
};

/* Драйвер компаратора аварійного струму */
class OvercurrentComparator {
private:
    struct Registers {
        volatile std::uint32_t CSR;
    };

    static Registers& regs() noexcept {
        return *reinterpret_cast<Registers*>(COMP_BASE);
    }

public:
    static void init(Hysteresis hyst) noexcept {
        constexpr std::uint32_t INPSEL_OPAMP    = (0x1UL << 7);
        constexpr std::uint32_t INMSEL_DAC1_CH1 = (0x4UL << 4);
        constexpr std::uint32_t COMP_EN         = (1UL << 0);
        constexpr std::uint32_t LOCK_BIT        = (1UL << 31);

        regs().CSR = static_cast<std::uint32_t>(hyst) |
                     INPSEL_OPAMP | INMSEL_DAC1_CH1 | COMP_EN;

        regs().CSR |= LOCK_BIT; // Апаратний захист від переконфігурації
    }
};

/* Керування аварійним гальмуванням ШІМ (TIM1 Break) */
class PwmBreakController {
private:
    struct Registers {
        volatile std::uint32_t CR1;
        volatile std::uint32_t RESERVED0[2];
        volatile std::uint32_t DIER;
        volatile std::uint32_t SR;
        volatile std::uint32_t RESERVED1[12];
        volatile std::uint32_t BDTR;
    };

    static Registers& regs() noexcept {
        return *reinterpret_cast<Registers*>(TIM1_BASE);
    }

public:
    static void enableBreakProtection(bool autoRestart = false) noexcept {
        constexpr std::uint32_t BKE = (1UL << 12);
        constexpr std::uint32_t AOE = (1UL << 14);
        constexpr std::uint32_t BIE = (1UL << 7);
        constexpr std::uint32_t MOE = (1UL << 15);

        std::uint32_t bdtrVal = regs().BDTR | BKE;
        if (autoRestart) bdtrVal |= AOE;
        else bdtrVal &= ~AOE;

        regs().BDTR = bdtrVal;
        regs().DIER |= BIE; // Дозвіл переривання
        regs().BDTR |= MOE; // Активація виходів
    }

    static bool isFaultActive() noexcept {
        return (regs().SR & (1UL << 7)) != 0;
    }

    static void clearFault() noexcept {
        regs().SR &= ~(1UL << 7);
    }

    static void rearmOutputs() noexcept {
        clearFault();
        regs().BDTR |= (1UL << 15); // MOE = 1
    }
};

/* Цифровий сторожовий пес АЦП */
class AnalogWatchdog {
private:
    struct Registers {
        volatile std::uint32_t ISR;
        volatile std::uint32_t IER;
        volatile std::uint32_t CR;
        volatile std::uint32_t CFGR;
        volatile std::uint32_t RESERVED[4];
        volatile std::uint32_t TR1;
    };

    static Registers& regs() noexcept {
        return *reinterpret_cast<Registers*>(ADC1_BASE);
    }

public:
    static void configureWindow(std::uint16_t lowThresh, std::uint16_t highThresh, std::uint8_t channel) noexcept {
        regs().TR1 = ((static_cast<std::uint32_t>(highThresh) & 0xFFFUL) << 16) |
                     (static_cast<std::uint32_t>(lowThresh) & 0xFFFUL);

        regs().CFGR |= (1UL << 23) | (static_cast<std::uint32_t>(channel & 0x1F) << 26);
        regs().IER  |= (1UL << 7); // AWD1IE
    }
};

} // namespace hw::analog
