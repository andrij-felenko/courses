#include <cstdint>
#include <span>

namespace hw {

// Базові адреси MMIO периферії
inline constexpr uintptr_t GpioOutAddr = 0x8000;
inline constexpr uintptr_t GpioInAddr  = 0x8001;

class GpioPort {
public:
    GpioPort() = delete;

    static void set_led(bool state) noexcept {
        auto& reg = *reinterpret_cast<volatile uint8_t*>(GpioOutAddr);
        if (state) {
            reg = static_cast<uint8_t>(reg | LedMask);
        } else {
            reg = static_cast<uint8_t>(reg & ~LedMask);
        }
    }

    [[nodiscard]] static bool is_button_pressed() noexcept {
        const auto& reg = *reinterpret_cast<const volatile uint8_t*>(GpioInAddr);
        return (reg & BtnMask) == 0;
    }

private:
    static constexpr uint8_t LedMask = 1U << 0;
    static constexpr uint8_t BtnMask = 1U << 0;
};

} // namespace hw
