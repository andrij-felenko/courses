#include <cstdint>
#include <concepts>
#include <span>
#include <optional>

namespace embedded::power {

// Базові адреси та маски регістрів скидання
inline constexpr std::uintptr_t rcc_base_address   = 0x40023800U;
inline constexpr std::uintptr_t rcc_csr_offset      = 0x74U;

inline constexpr std::uint32_t csr_rmvf_mask       = 1U << 24;
inline constexpr std::uint32_t csr_borrstf_mask    = 1U << 25;
inline constexpr std::uint32_t csr_pinrstf_mask    = 1U << 26;
inline constexpr std::uint32_t csr_porrstf_mask    = 1U << 27;
inline constexpr std::uint32_t csr_sftrstf_mask    = 1U << 28;
inline constexpr std::uint32_t csr_iwdgrstf_mask   = 1U << 29;

inline constexpr std::uint32_t magic_token_value   = 0x5A2C9B1EU;
inline constexpr std::uint32_t max_consecutive_bor = 3U;

enum class ResetReason : std::uint8_t {
    Unknown,
    ColdPowerOn,
    Brownout,
    ExternalPin,
    Software,
    Watchdog
};

struct DiagnosticReport {
    ResetReason   reason;
    std::uint32_t consecutive_bor_count;
    bool          is_degraded_recovery_active;
    std::uint8_t  throttle_limit_percent;
};

// Енергонезалежний контекст у пам'яті .noinit
struct PersistentContext {
    std::uint32_t magic_token;
    std::uint32_t bor_counter;
};

// Розміщення в секції пам'яті, що не ініціалізується стартапом
[[gnu::section(".noinit")]] volatile PersistentContext g_persistent_state;

class PowerSupervisor {
public:
    static auto initialize() noexcept -> DiagnosticReport {
        auto* const csr_register = reinterpret_cast<volatile std::uint32_t*>(
            rcc_base_address + rcc_csr_offset
        );
        
        const std::uint32_t csr_snapshot = *csr_register;
        
        // Очищення апаратних прапорців
        *csr_register |= csr_rmvf_mask;

        // Перевірка цілісності SRAM
        if (g_persistent_state.magic_token != magic_token_value) {
            g_persistent_state.magic_token = magic_token_value;
            g_persistent_state.bor_counter = 0U;
        }

        ResetReason detected_reason = ResetReason::Unknown;

        if ((csr_snapshot & csr_borrstf_mask) != 0U) {
            detected_reason = ResetReason::Brownout;
            g_persistent_state.bor_counter++;
        } else if ((csr_snapshot & csr_porrstf_mask) != 0U) {
            detected_reason = ResetReason::ColdPowerOn;
            g_persistent_state.bor_counter = 0U;
        } else if ((csr_snapshot & csr_iwdgrstf_mask) != 0U) {
            detected_reason = ResetReason::Watchdog;
        } else if ((csr_snapshot & csr_sftrstf_mask) != 0U) {
            detected_reason = ResetReason::Software;
        } else if ((csr_snapshot & csr_pinrstf_mask) != 0U) {
            detected_reason = ResetReason::ExternalPin;
            g_persistent_state.bor_counter = 0U;
        }

        const bool is_degraded = (g_persistent_state.bor_counter >= max_consecutive_bor);
        const std::uint8_t limit = is_degraded ? 25U : 100U;

        return DiagnosticReport{
            .reason                      = detected_reason,
            .consecutive_bor_count       = g_persistent_state.bor_counter,
            .is_degraded_recovery_active = is_degraded,
            .throttle_limit_percent      = limit
        };
    }

    static void mark_system_healthy() noexcept {
        g_persistent_state.bor_counter = 0U;
    }
};

class SafeActuatorDriver {
public:
    explicit constexpr SafeActuatorDriver(const DiagnosticReport& report) noexcept
        : max_limit_{report.throttle_limit_percent} {}

    void ramp_to(std::uint8_t requested_pwm_percent) const noexcept {
        const std::uint8_t target = (requested_pwm_percent > max_limit_) 
                                  ? max_limit_ 
                                  : requested_pwm_percent;

        // Плавний розгін із контролем кроку наростання
        for (std::uint8_t step = 0U; step <= target; step += 5U) {
            set_hardware_pwm(step);
            busy_wait_us(1000U);
        }
    }

private:
    static void set_hardware_pwm(std::uint8_t duty) noexcept {
        // Запис у таймер керування силовим ключем
        static_cast<void>(duty);
    }

    static void busy_wait_us(std::uint32_t us) noexcept {
        for (volatile std::uint32_t i = 0; i < us * 16U; ++i) {
            asm volatile("nop");
        }
    }

    std::uint8_t max_limit_{100U};
};

} // namespace embedded::power
