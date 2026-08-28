#include <cstdint>
#include <expected>
#include <concepts>
#include <span>

namespace Hardware::Power {

/* Регістри підсистеми керування живленням (PWR / SMPS) */
struct PwrRegisters {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t CR3;
    volatile uint32_t CR4;
    volatile uint32_t CR5;
    volatile uint32_t SR1;
    volatile uint32_t SR2;
};

inline auto* const PWR_REGS = reinterpret_cast<PwrRegisters*>(0x58000400UL);

enum class Error : uint8_t {
    Timeout,
    InductorMissing,
    VoltageFault,
    InvalidConfiguration
};

enum class CoreSupply : uint8_t {
    MainLdo,
    IntegratedDcdc,
    UltraLowPowerLdo
};

enum class InductorCurrentLimit : uint8_t {
    Limit100mA = 0,
    Limit150mA = 1,
    Limit200mA = 2,
    Limit300mA = 3
};

enum class VoltageScale : uint8_t {
    HighPerformance = 1, // 1.2 В
    EnergySaving    = 2  // 1.0 В
};

class CorePowerManager {
public:
    CorePowerManager() = default;
    ~CorePowerManager() = default;

    /* Заборона копіювання контролера живлення */
    CorePowerManager(const CorePowerManager&) = delete;
    CorePowerManager& operator=(const CorePowerManager&) = delete;

    /**
     * @brief Запуск вбудованого DC-DC регулятора ядра з контролем стабілізації.
     */
    [[nodiscard]] std::expected<void, Error> enableDcdc(
        InductorCurrentLimit limit = InductorCurrentLimit::Limit200mA,
        uint32_t maxWaitIterations = 100000) noexcept {
        constexpr uint32_t CR5_SMPSEN_MASK = (1UL << 0);
        constexpr uint32_t CR5_BORH_MASK   = (1UL << 8);
        constexpr uint32_t CR5_ILMP_SHIFT  = 16;
        constexpr uint32_t CR5_ILMP_MASK   = (3UL << CR5_ILMP_SHIFT);
        constexpr uint32_t SR2_RDY_MASK    = (1UL << 0);

        if ((PWR_REGS->CR5 & CR5_SMPSEN_MASK) && (PWR_REGS->SR2 & SR2_RDY_MASK)) {
            return {};
        }

        /* Конфігурація струмового захисту дроселя */
        uint32_t cr5 = PWR_REGS->CR5;
        cr5 &= ~CR5_ILMP_MASK;
        cr5 |= (static_cast<uint32_t>(limit) << CR5_ILMP_SHIFT);
        PWR_REGS->CR5 = cr5;

        /* Активація захисту від просідання напруги батареї */
        PWR_REGS->CR5 |= CR5_BORH_MASK;
        PWR_REGS->CR5 |= CR5_SMPSEN_MASK;

        while (!(PWR_REGS->SR2 & SR2_RDY_MASK)) {
            if (--maxWaitIterations == 0) {
                PWR_REGS->CR5 &= ~CR5_SMPSEN_MASK;
                return std::unexpected(Error::Timeout);
            }
        }

        currentSupply_ = CoreSupply::IntegratedDcdc;
        return {};
    }

    /**
     * @brief Переведення живлення на LDO.
     */
    void enableLdo() noexcept {
        constexpr uint32_t CR5_SMPSEN_MASK = (1UL << 0);
        PWR_REGS->CR5 &= ~CR5_SMPSEN_MASK;
        currentSupply_ = CoreSupply::MainLdo;
    }

    /**
     * @brief Налаштування динамічного масштабування напруги ядра (DVS).
     */
    void setVoltageScale(VoltageScale scale) noexcept {
        constexpr uint32_t CR1_VOS_SHIFT = 9;
        constexpr uint32_t CR1_VOS_MASK  = (3UL << CR1_VOS_SHIFT);

        uint32_t cr1 = PWR_REGS->CR1;
        cr1 &= ~CR1_VOS_MASK;
        cr1 |= (static_cast<uint32_t>(scale) << CR1_VOS_SHIFT);
        PWR_REGS->CR1 = cr1;
    }

    /**
     * @brief Вхід у режим глибокого сну з використанням RAII-гарантії відновлення.
     */
    void executeDeepSleep() noexcept {
        constexpr uint32_t CR1_LPR_MASK    = (1UL << 14);
        constexpr uint32_t CR5_SMPSEN_MASK = (1UL << 0);

        /* Перехід на ULP-LDO та вимкнення DC-DC */
        PWR_REGS->CR1 |= CR1_LPR_MASK;
        PWR_REGS->CR5 &= ~CR5_SMPSEN_MASK;

        __asm volatile ("dsb");
        __asm volatile ("wfi");
        __asm volatile ("isb");

        /* Відновлення після пробудження */
        PWR_REGS->CR1 &= ~CR1_LPR_MASK;
        currentSupply_ = CoreSupply::MainLdo;
    }

    [[nodiscard]] CoreSupply activeSupply() const noexcept {
        return currentSupply_;
    }

private:
    CoreSupply currentSupply_{CoreSupply::MainLdo};
};

/**
 * @brief RAII-обгортка для тимчасового перемикання на малошумний режим LDO
 * (наприклад, на час виконання прецизійного вимірювання АЦП).
 */
class ScopedQuietLdoMode {
public:
    explicit ScopedQuietLdoMode(CorePowerManager& manager) noexcept
        : manager_(manager), previousSupply_(manager.activeSupply()) {
        if (previousSupply_ == CoreSupply::IntegratedDcdc) {
            manager_.enableLdo();
        }
    }

    ~ScopedQuietLdoMode() noexcept {
        if (previousSupply_ == CoreSupply::IntegratedDcdc) {
            (void)manager_.enableDcdc();
        }
    }

    ScopedQuietLdoMode(const ScopedQuietLdoMode&) = delete;
    ScopedQuietLdoMode& operator=(const ScopedQuietLdoMode&) = delete;

private:
    CorePowerManager& manager_;
    CoreSupply previousSupply_;
};

} // namespace Hardware::Power
