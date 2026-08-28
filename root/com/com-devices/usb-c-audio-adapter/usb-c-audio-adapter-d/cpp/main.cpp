#include <cstdint>
#include <span>

namespace usb_c {

enum class CcState : std::uint8_t {
    Open = 0x00,
    Ra   = 0x01,
    Rd   = 0x02
};

struct TcpciRegisters {
    static constexpr std::uint8_t RoleControl = 0x1A;
    static constexpr std::uint8_t CcStatus    = 0x1D;
};

struct AudioSwitchRegisters {
    static constexpr std::uint8_t Control     = 0x02;
    static constexpr std::uint8_t SwitchEn    = 1 << 7;
    static constexpr std::uint8_t ModeAudio   = 2 << 5;
    static constexpr std::uint8_t NegPumpEn   = 1 << 0;
};

class PortManager {
public:
    explicit PortManager(class II2cBus& bus) : bus_(bus) {}

    void handleAttachInterrupt() {
        const std::uint8_t status = readRegister(TcpciRegisters::CcStatus);
        const auto cc1 = static_cast<CcState>(status & 0x03);
        const auto cc2 = static_cast<CcState>((status >> 2) & 0x03);

        if (cc1 == CcState::Ra && cc2 == CcState::Ra) {
            configureAnalogAudioMode();
        }
    }

private:
    class II2cBus& bus_;

    std::uint8_t readRegister(std::uint8_t reg);
    void writeRegister(std::uint8_t devAddr, std::uint8_t reg, std::uint8_t val);

    void configureAnalogAudioMode() {
        constexpr std::uint8_t config = AudioSwitchRegisters::SwitchEn |
                                       AudioSwitchRegisters::ModeAudio |
                                       AudioSwitchRegisters::NegPumpEn;
        writeRegister(0x42, AudioSwitchRegisters::Control, config);
    }
};

} // namespace usb_c
