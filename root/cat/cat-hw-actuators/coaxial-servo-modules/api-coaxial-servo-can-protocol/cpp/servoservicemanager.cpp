#include <cstdint>
#include <array>

class ServoServiceManager {
public:
    enum class Mode : uint8_t {
        Control    = 0x00,
        Enable     = 0x01,
        Disable    = 0x02,
        SetZero    = 0x03,
        ClearFault = 0x04
    };

    static uint32_t makeCanId(Mode mode, uint8_t targetId, uint8_t masterId) {
        return ((static_cast<uint32_t>(mode) & 0x1F) << 24) |
               ((static_cast<uint32_t>(targetId) & 0xFF) << 8) |
                (static_cast<uint32_t>(masterId) & 0xFF);
    }

    static bool hasHardwareFault(uint8_t statusByte) {
        return (statusByte & 0x0F) != 0;
    }

    static std::array<uint8_t, 8> createZeroCalibrationPayload() {
        return {0, 0, 0, 0, 0, 0, 0, 0};
    }

    static std::array<uint8_t, 8> createClearFaultsPayload() {
        return {0, 0, 0, 0, 0, 0, 0, 0};
    }
};
