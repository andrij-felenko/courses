// PowerDomainController.hpp — Ідіоматична C++20 обгортка керування живленням SoC
#pragma once
#include <cstdint>
#include <span>
#include <expected>
#include <array>
#include <string_view>

namespace soc::pmc {

enum class PmcError : uint8_t {
    PowerGoodTimeout,
    PmicCommunicationFailed,
    InvalidOppLevel,
    DomainAlreadyActive,
    DomainAlreadyOff
};

enum class OppLevel : uint8_t {
    Low = 0,
    Nominal = 1,
    High = 2,
    Turbo = 3
};

struct OppPoint {
    uint32_t freq_khz;
    uint32_t voltage_uv;
    uint32_t settle_delay_us;
};

class PowerDomainController {
public:
    static constexpr std::array<OppPoint, 4> OppTable = {{
        {  400'000,  650'000, 20 },
        { 1'200'000,  750'000, 25 },
        { 2'000'000,  900'000, 35 },
        { 2'800'000, 1'050'000, 50 }
    }};

    explicit constexpr PowerDomainController(uintptr_t base_address) noexcept
        : base_addr_{base_address} {}

    // Керування доменом живлення
    [[nodiscard]] std::expected<void, PmcError> power_up() const noexcept {
        // Крок 1: Ізоляція
        write_reg(RegOffset::IsoCtrl, BitMask::IsoEnable);

        // Крок 2: Перший ступінь ключів (захист від dI/dt)
        write_reg(RegOffset::PwrGateCtrl, BitMask::PwrStage1);

        // Крок 3: Очікування сигналу Power Good
        if (!wait_for_bit(RegOffset::PwrGateStatus, BitMask::PwrGood, 100'000)) {
            write_reg(RegOffset::PwrGateCtrl, 0); // Аварійне вимкнення
            return std::unexpected(PmcError::PowerGoodTimeout);
        }

        // Крок 4: Другий ступінь силових ключів
        write_reg(RegOffset::PwrGateCtrl, BitMask::PwrStage1 | BitMask::PwrStage2);

        // Крок 5: Відновлення Retention
        write_reg(RegOffset::RetCtrl, BitMask::RetRestore);
        busy_delay(500);
        write_reg(RegOffset::RetCtrl, 0);

        // Крок 6: Зняття ізоляції
        write_reg(RegOffset::IsoCtrl, 0);

        // Крок 7: Тактування
        write_reg(RegOffset::ClkGateCtrl, BitMask::ClkEnable);

        // Крок 8: Деактивація скидання
        write_reg(RegOffset::ResetCtrl, BitMask::ResetDeassert);

        return {};
    }

    [[nodiscard]] std::expected<void, PmcError> power_down() const noexcept {
        write_reg(RegOffset::ResetCtrl, 0);
        write_reg(RegOffset::ClkGateCtrl, 0);

        write_reg(RegOffset::RetCtrl, BitMask::RetSave);
        busy_delay(500);
        write_reg(RegOffset::RetCtrl, 0);

        write_reg(RegOffset::IsoCtrl, BitMask::IsoEnable);
        write_reg(RegOffset::PwrGateCtrl, 0);

        return {};
    }

    // Безпечний перехід DVFS
    [[nodiscard]] std::expected<void, PmcError> set_opp(OppLevel current, OppLevel target) const noexcept {
        if (current == target) {
            return {};
        }

        const auto curr_idx = static_cast<size_t>(current);
        const auto targ_idx = static_cast<size_t>(target);

        if (targ_idx >= OppTable.size()) {
            return std::unexpected(PmcError::InvalidOppLevel);
        }

        const auto& target_pt = OppTable[targ_idx];

        if (targ_idx > curr_idx) {
            // Scale UP: 1. Напруга -> 2. Затримка -> 3. Частота
            if (!set_pmic_voltage(target_pt.voltage_uv)) {
                return std::unexpected(PmcError::PmicCommunicationFailed);
            }
            busy_delay(target_pt.settle_delay_us * 100);
            write_reg(RegOffset::ClkGateCtrl, target_pt.freq_khz / 1'000);
        } else {
            // Scale DOWN: 1. Частота -> 2. Напруга
            write_reg(RegOffset::ClkGateCtrl, target_pt.freq_khz / 1'000);
            if (!set_pmic_voltage(target_pt.voltage_uv)) {
                return std::unexpected(PmcError::PmicCommunicationFailed);
            }
            busy_delay(target_pt.settle_delay_us * 100);
        }

        return {};
    }

private:
    enum class RegOffset : uintptr_t {
        PwrGateCtrl   = 0x00,
        PwrGateStatus = 0x04,
        IsoCtrl       = 0x08,
        RetCtrl       = 0x0C,
        ClkGateCtrl   = 0x10,
        ResetCtrl     = 0x14,
        PmicVoltCmd   = 0x18
    };

    struct BitMask {
        static constexpr uint32_t PwrStage1     = (1U << 0);
        static constexpr uint32_t PwrStage2     = (1U << 1);
        static constexpr uint32_t PwrGood       = (1U << 0);
        static constexpr uint32_t IsoEnable     = (1U << 0);
        static constexpr uint32_t RetSave       = (1U << 0);
        static constexpr uint32_t RetRestore    = (1U << 1);
        static constexpr uint32_t ClkEnable     = (1U << 0);
        static constexpr uint32_t ResetDeassert = (1U << 0);
    };

    uintptr_t base_addr_{0};

    void write_reg(RegOffset offset, uint32_t val) const noexcept {
        *reinterpret_cast<volatile uint32_t*>(base_addr_ + static_cast<uintptr_t>(offset)) = val;
    }

    [[nodiscard]] uint32_t read_reg(RegOffset offset) const noexcept {
        return *reinterpret_cast<const volatile uint32_t*>(base_addr_ + static_cast<uintptr_t>(offset));
    }

    [[nodiscard]] bool wait_for_bit(RegOffset offset, uint32_t mask, uint32_t timeout) const noexcept {
        while ((read_reg(offset) & mask) == 0U) {
            if (--timeout == 0) return false;
        }
        return true;
    }

    [[nodiscard]] bool set_pmic_voltage(uint32_t microvolts) const noexcept {
        write_reg(RegOffset::PmicVoltCmd, microvolts);
        return wait_for_bit(RegOffset::PwrGateStatus, 0x02U, 500'000);
    }

    static void busy_delay(uint32_t cycles) noexcept {
        for (volatile uint32_t i = 0; i < cycles; ++i) {
            asm volatile("" ::: "memory");
        }
    }
};

// RAII Guard для автоматичного керування життєвим циклом домену
class PowerDomainGuard {
public:
    explicit PowerDomainGuard(const PowerDomainController& controller)
        : controller_{controller} {
        is_active_ = controller_.power_up().has_value();
    }

    ~PowerDomainGuard() noexcept {
        if (is_active_) {
            (void)controller_.power_down();
        }
    }

    PowerDomainGuard(const PowerDomainGuard&) = delete;
    PowerDomainGuard& operator=(const PowerDomainGuard&) = delete;
    PowerDomainGuard(PowerDomainGuard&& other) noexcept
        : controller_{other.controller_}, is_active_{other.is_active_} {
        other.is_active_ = false;
    }

    [[nodiscard]] bool is_powered() const noexcept { return is_active_; }

private:
    const PowerDomainController& controller_;
    bool is_active_{false};
};

} // namespace soc::pmc
