#include <cstdint>
#include <expected>

namespace hw {

/* Регістри контролера тактування та скидання (RCC) */
inline constexpr std::uintptr_t rcc_base = 0x40023800U;

struct RccRegisters {
    volatile std::uint32_t cr;
    volatile std::uint32_t pllcfgr;
    volatile std::uint32_t cfgr;
    volatile std::uint32_t cir;
    volatile std::uint32_t ahb1rstr;
    volatile std::uint32_t ahb2rstr;
    volatile std::uint32_t reserved[20];
    volatile std::uint32_t csr;
};

inline auto& rcc() noexcept {
    return *reinterpret_cast<RccRegisters*>(rcc_base);
}

enum class ResetCause : std::uint8_t {
    ColdPowerOn,
    ExternalPinReset,
    Other
};

enum class ClockError : std::uint8_t {
    HseOscillatorTimeout,
    SwitchFailed
};

class SystemStartup {
public:
    static constexpr std::uint32_t hse_timeout_cycles = 0x5000U;

    [[nodiscard]] static ResetCause diagnose_and_clear_reset_flags() noexcept {
        const std::uint32_t csr_val = rcc().csr;
        ResetCause cause = ResetCause::Other;

        if ((csr_val & (1U << 27)) != 0) {
            cause = ResetCause::ColdPowerOn;
        } else if ((csr_val & (1U << 26)) != 0) {
            cause = ResetCause::ExternalPinReset;
        }

        rcc().csr |= (1U << 24); // Очистити прапорці скидання (RMVF)
        return cause;
    }

    [[nodiscard]] static std::expected<void, ClockError> init_hse_clock() noexcept {
        // 1. Забезпечити роботу резервного генератора HSI
        rcc().cr |= (1U << 0);
        while ((rcc().cr & (1U << 1)) == 0) {}

        // 2. Увімкнути живлення генератора HSE
        rcc().cr |= (1U << 16);

        // 3. Очікування виходу резонатора на стабільну амплітуду
        std::uint32_t timeout = hse_timeout_cycles;
        while (((rcc().cr & (1U << 17)) == 0) && (--timeout > 0)) {}

        if (timeout == 0) {
            rcc().cr &= ~(1U << 16); // Вимкнути несправний HSE
            return std::unexpected(ClockError::HseOscillatorTimeout);
        }

        // 4. Перемикання джерела SYSCLK на HSE
        rcc().cfgr = (rcc().cfgr & ~0x03U) | 0x01U;

        // 5. Очікування підтвердження комутатора
        while ((rcc().cfgr & (0x03U << 2)) != (0x01U << 2)) {}

        // 6. Увімкнення апаратного супервізора частоти (CSS)
        rcc().cr |= (1U << 19);

        return {};
    }
};

} // namespace hw
