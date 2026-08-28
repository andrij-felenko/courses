#include <cstdint>
#include <span>
#include <concepts>

enum class PortType : uint8_t {
    Unknown = 0,
    SDP     = 1,
    CDP     = 2,
    DCP     = 3,
    Apple   = 4,
    Samsung = 5
};

struct ChargerProfile {
    uint16_t maxCurrentMa;
    bool allowData;
};

class UsbBatteryChargingDetector {
public:
    static constexpr uint8_t RegBcStatus = 0x01;
    static constexpr uint8_t RegBcCtrl   = 0x02;

    virtual ~UsbBatteryChargingDetector() = default;

    virtual uint8_t readRegister(uint8_t reg) = 0;
    virtual void writeRegister(uint8_t reg, uint8_t val) = 0;
    virtual void applyCurrentLimit(uint16_t currentMa) = 0;
    virtual void setUsbDataEnabled(bool enabled) = 0;

    void handleInterrupt() {
        const uint8_t status = readRegister(RegBcStatus);
        const bool vbusValid = (status & (1 << 7)) != 0;
        const bool detectionDone = (status & (1 << 0)) != 0;

        if (!vbusValid) {
            applyCurrentLimit(0);
            setUsbDataEnabled(false);
            return;
        }

        if (detectionDone) {
            const auto port = static_cast<PortType>((status >> 4) & 0x07);
            const auto profile = resolveProfile(port);
            applyCurrentLimit(profile.maxCurrentMa);
            setUsbDataEnabled(profile.allowData);
        }
    }

private:
    [[nodiscard]] static constexpr ChargerProfile resolveProfile(PortType port) noexcept {
        switch (port) {
            case PortType::SDP:     return { 500,  true  };
            case PortType::CDP:     return { 1500, true  };
            case PortType::DCP:     return { 1500, false };
            case PortType::Apple:   return { 2400, false };
            case PortType::Samsung: return { 2000, false };
            default:                return { 100,  false };
        }
    }
};
