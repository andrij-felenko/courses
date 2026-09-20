#include <cstdint>
#include <cstddef>

struct SystemConfig {
    std::uint8_t i2cAddress{0};
    bool highSpeedMode{false};
    std::uint8_t operationMode{0};
    bool parityEnable{false};

    static constexpr std::uint8_t MaskI2cAddr   = 0x0F;
    static constexpr std::uint8_t MaskSpeedMode = 0x10;
    static constexpr std::uint8_t MaskOperMode  = 0x60;
    static constexpr std::uint8_t MaskParityEn  = 0x80;

    static SystemConfig parse(std::uint8_t rawGpioByte) noexcept {
        const std::uint8_t activeHigh = static_cast<std::uint8_t>(~rawGpioByte);
        
        return SystemConfig{
            .i2cAddress     = static_cast<std::uint8_t>(activeHigh & MaskI2cAddr),
            .highSpeedMode  = (activeHigh & MaskSpeedMode) != 0,
            .operationMode  = static_cast<std::uint8_t>((activeHigh & MaskOperMode) >> 5),
            .parityEnable   = (activeHigh & MaskParityEn) != 0
        };
    }
};
