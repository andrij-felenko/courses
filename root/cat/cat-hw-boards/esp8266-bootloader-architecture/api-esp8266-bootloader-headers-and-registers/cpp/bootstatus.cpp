#include <cstdint>

class BootStatus {
public:
    static constexpr std::uintptr_t RtcStore0Addr = 0x60001200;
    static constexpr std::uintptr_t RtcStateAddr  = 0x60000b00;

    static std::uint8_t getResetReason() noexcept {
        auto* stateReg = reinterpret_cast<volatile std::uint32_t*>(RtcStateAddr);
        return static_cast<std::uint8_t>(*stateReg & 0x0FU);
    }

    static void setFastBootVector(std::uint32_t entryPoint) noexcept {
        auto* storeReg = reinterpret_cast<volatile std::uint32_t*>(RtcStore0Addr);
        *storeReg = entryPoint;
    }
};
