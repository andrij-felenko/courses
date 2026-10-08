#include <cstdint>

enum class SystemFault : uint8_t {
    None = 0,
    LowVoltage,
    PdFail,
    TipDisconnected,
    ThermalRunaway
};

struct HardwareStatus {
    uint16_t vinMv{0};
    uint16_t vCutoffMv{9000};
    int16_t tipTempC{0};
    bool pdNegotiated{false};
    bool sensorValid{false};
};

class SystemDiagnosticsManager {
public:
    [[nodiscard]] SystemFault diagnose(const HardwareStatus& status) const noexcept {
        if (!status.sensorValid || status.tipTempC < -20 || status.tipTempC > 500) {
            return SystemFault::TipDisconnected;
        }

        if (status.vinMv < status.vCutoffMv) {
            return SystemFault::LowVoltage;
        }

        if (!status.pdNegotiated && status.vinMv < 9000) {
            return SystemFault::PdFail;
        }

        return SystemFault::None;
    }
};
