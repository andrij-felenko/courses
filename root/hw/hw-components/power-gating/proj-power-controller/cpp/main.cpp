#include <cstdint>
#include <expected>
#include <span>
#include <chrono>

enum class PowerDomain : uint32_t {
    Gpu = 0,
    Npu = 1,
    Dsp = 2,
    Max
};

enum class PowerError {
    Timeout,
    InvalidDomain,
    HardwareFault
};

class PowerManager {
public:
    static constexpr uintptr_t PmuBaseAddr = 0x4000E000U;

    static std::expected<void, PowerError> setDomainPower(PowerDomain domain, bool enable) noexcept {
        if (domain >= PowerDomain::Max) {
            return std::unexpected(PowerError::InvalidDomain);
        }

        const auto domainIdx = static_cast<uint32_t>(domain);
        auto* const reqReg  = reinterpret_cast<volatile uint32_t*>(PmuBaseAddr + 0x10U + (domainIdx * 8U));
        auto* const statReg = reinterpret_cast<const volatile uint32_t*>(PmuBaseAddr + 0x14U + (domainIdx * 8U));

        // Ініціація апаратного переходу FSM
        *reqReg = enable ? 1U : 0U;

        // Полінг підтвердження стабілізації домену з лімітом спроб
        constexpr uint32_t MaxAttempts = 100'000U;
        constexpr uint32_t AckMask     = (1U << 0);
        constexpr uint32_t BusyMask    = (1U << 1);

        for (uint32_t i = 0; i < MaxAttempts; ++i) {
            const uint32_t status = *statReg;
            if ((status & AckMask) != 0U && (status & BusyMask) == 0U) {
                return {};
            }
        }

        return std::unexpected(PowerError::Timeout);
    }
};

/**
 * RAII-обгортка для безпечного виконання обчислень у виділеному домені живлення.
 * Автоматично вмикає живлення при створенні об'єкта та гарантує
 * безпечне вимкнення живлення при виході зі скоупу функцій.
 */
class ScopedPowerDomain {
public:
    explicit ScopedPowerDomain(PowerDomain domain) 
        : domain_(domain), active_(false) {
        if (PowerManager::setDomainPower(domain_, true).has_value()) {
            active_ = true;
        }
    }

    ~ScopedPowerDomain() noexcept {
        if (active_) {
            PowerManager::setDomainPower(domain_, false);
        }
    }

    [[nodiscard]] bool isReady() const noexcept { return active_; }

    ScopedPowerDomain(const ScopedPowerDomain&) = delete;
    ScopedPowerDomain& operator=(const ScopedPowerDomain&) = delete;
    ScopedPowerDomain(ScopedPowerDomain&& other) noexcept 
        : domain_(other.domain_), active_(other.active_) {
        other.active_ = false;
    }

private:
    PowerDomain domain_;
    bool active_;
};
