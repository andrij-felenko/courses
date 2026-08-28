// ship_mode_controller.hpp - Ідіоматична реалізація мовою C++20
#pragma once

#include <cstdint>
#include <concepts>
#include <expected>
#include <chrono>

namespace power::transport {

enum class ErrorCode : uint8_t {
    VoltageTooHigh,     // Перевищує нормативні 30% SoC (UN 3480)
    VoltageTooLow,      // Загроза мідного розчинення (< 3.50 В)
    VBusActive,         // Зарядний пристрій підключено
    HardwareBusError    // Помилка шини зв'язку PMIC
};

template <typename HardwareInterface>
concept PowerManager = requires(HardwareInterface hw, uint8_t addr, uint8_t reg, uint8_t val) {
    { hw.readVoltageMillivolts() } -> std::same_as<uint32_t>;
    { hw.isExternalPowerConnected() } -> std::same_as<bool>;
    { hw.writeRegister(addr, reg, val) } -> std::same_as<bool>;
    { hw.readRegister(addr, reg) } -> std::same_as<std::expected<uint8_t, ErrorCode>>;
};

class ShipModeController {
public:
    static constexpr uint32_t kMaxTransportVoltageMv = 3800; // 30% SoC limit
    static constexpr uint32_t kMinTransportVoltageMv = 3500; // Critical floor
    static constexpr uint8_t  kPmicPowerConfigReg    = 0x05;
    static constexpr uint8_t  kBitEnterShipMode      = 1 << 6;
    static constexpr uint8_t  kBitWakeDebounce3s     = 1 << 4;

    explicit constexpr ShipModeController(uint8_t pmicI2cAddress) noexcept
        : pmicAddress_{pmicI2cAddress} {}

    template <PowerManager Interface>
    [[nodiscard]] std::expected<void, ErrorCode> verifyPreconditions(Interface& hw) const noexcept {
        if (hw.isExternalPowerConnected()) {
            return std::unexpected(ErrorCode::VBusActive);
        }

        const uint32_t voltage = hw.readVoltageMillivolts();
        if (voltage > kMaxTransportVoltageMv) {
            return std::unexpected(ErrorCode::VoltageTooHigh);
        }
        if (voltage < kMinTransportVoltageMv) {
            return std::unexpected(ErrorCode::VoltageTooLow);
        }

        return {};
    }

    template <PowerManager Interface>
    [[nodiscard]] std::expected<void, ErrorCode> executeShipMode(Interface& hw) const noexcept {
        auto check = verifyPreconditions(hw);
        if (!check) {
            return check;
        }

        auto currentReg = hw.readRegister(pmicAddress_, kPmicPowerConfigReg);
        if (!currentReg) {
            return std::unexpected(ErrorCode::HardwareBusError);
        }

        uint8_t newConfig = *currentReg | kBitWakeDebounce3s | kBitEnterShipMode;
        if (!hw.writeRegister(pmicAddress_, kPmicPowerConfigReg, newConfig)) {
            return std::unexpected(ErrorCode::HardwareBusError);
        }

        // Чекаємо апаратного знеструмлення контролером PMIC
        while (true) {
            // Low-power sleep barrier
        }

        return {};
    }

private:
    uint8_t pmicAddress_;
};

} // namespace power::transport
