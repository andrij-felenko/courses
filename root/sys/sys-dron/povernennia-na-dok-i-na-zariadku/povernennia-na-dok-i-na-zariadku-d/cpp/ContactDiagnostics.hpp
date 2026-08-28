// ContactDiagnostics.hpp
#pragma once
#include <cstdint>
#include <optional>
#include <span>
#include <chrono>

namespace DroneDock {

enum class ContactState : uint8_t {
    Open,
    Probing,
    PolarityFault,
    HighResistance,
    CommTimeout,
    ReadyToCharge,
    ChargingActive,
    ThermalFault
};

struct DiagnosticTelemetry {
    float senseVoltageDropMv{0.0F};
    float probeCurrentMa{0.0F};
    float calculatedResistanceMohm{0.0F};
    uint32_t batteryVoltageMv{0};
    float maxCellTempC{0.0F};
    bool reversePolarityDetected{false};
    bool bmsHeartbeatAlive{false};
};

class DockChargeController {
public:
    static constexpr float MaxAllowedResistanceMohm{40.0F};
    static constexpr uint32_t MinBatteryVoltageMv{18000};
    static constexpr uint32_t MaxBatteryVoltageMv{25500};
    static constexpr float MaxCellTemperatureC{45.0F};
    static constexpr std::chrono::milliseconds CommTimeoutLimit{1000};

    constexpr DockChargeController() = default;

    [[nodiscard]] ContactState getState() const noexcept { return currentState_; }

    ContactState update(const DiagnosticTelemetry& telem,
                        std::chrono::milliseconds currentTime) noexcept
    {
        switch (currentState_) {
        case ContactState::Open:
            if (telem.probeCurrentMa > 50.0F) {
                currentState_ = ContactState::Probing;
                stateEntryTime_ = currentTime;
            }
            break;

        case ContactState::Probing:
            if (telem.reversePolarityDetected) {
                currentState_ = ContactState::PolarityFault;
                break;
            }

            if (telem.probeCurrentMa > 10.0F) {
                const float rMohm = (telem.senseVoltageDropMv / telem.probeCurrentMa) * 1000.0F;
                if (rMohm > MaxAllowedResistanceMohm) {
                    currentState_ = ContactState::HighResistance;
                    break;
                }
            }

            if (!telem.bmsHeartbeatAlive) {
                if (currentTime - stateEntryTime_ > CommTimeoutLimit) {
                    currentState_ = ContactState::CommTimeout;
                }
                break;
            }

            if (telem.batteryVoltageMv < MinBatteryVoltageMv ||
                telem.batteryVoltageMv > MaxBatteryVoltageMv) {
                currentState_ = ContactState::PolarityFault;
                break;
            }

            if (telem.maxCellTempC > MaxCellTemperatureC) {
                currentState_ = ContactState::ThermalFault;
                break;
            }

            currentState_ = ContactState::ReadyToCharge;
            break;

        case ContactState::ReadyToCharge:
            // Очікування сигналу запуску від планувальника заряду
            break;

        case ContactState::ChargingActive:
            if (telem.maxCellTempC > MaxCellTemperatureC || !telem.bmsHeartbeatAlive) {
                currentState_ = ContactState::ThermalFault;
            }
            break;

        case ContactState::PolarityFault:
        case ContactState::HighResistance:
        case ContactState::CommTimeout:
        case ContactState::ThermalFault:
            // Стан аварійної ізоляції контактів
            break;
        }

        return currentState_;
    }

    void setChargingActive() noexcept {
        if (currentState_ == ContactState::ReadyToCharge) {
            currentState_ = ContactState::ChargingActive;
        }
    }

    void reset() noexcept {
        currentState_ = ContactState::Open;
        stateEntryTime_ = std::chrono::milliseconds{0};
    }

private:
    ContactState currentState_{ContactState::Open};
    std::chrono::milliseconds stateEntryTime_{0};
};

} // namespace DroneDock
