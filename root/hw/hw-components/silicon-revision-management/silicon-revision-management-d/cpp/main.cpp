// silicon_quirk_dispatch.hpp - Ідіоматична реалізація мовою C++20
#include <cstdint>
#include <array>
#include <optional>

namespace hardware {

enum class Quirk : uint32_t {
    None             = 0,
    I2cBusyLock      = (1U << 0),
    UartDmaCorrupt   = (1U << 1),
    AdcRefDrift      = (1U << 2),
};

constexpr Quirk operator|(Quirk a, Quirk b) noexcept {
    return static_cast<Quirk>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr Quirk operator&(Quirk a, Quirk b) noexcept {
    return static_cast<Quirk>(static_cast<uint32_t>(a) & static_cast<uint32_t>(b));
}

struct QuirkEntry {
    uint16_t rev_id;
    Quirk quirks;
};

class SiliconQuirkManager {
public:
    explicit constexpr SiliconQuirkManager(uint16_t rev_id) noexcept {
        for (const auto& entry : Registry) {
            if (entry.rev_id == rev_id) {
                active_quirks_ = entry.quirks;
                return;
            }
        }
    }

    [[nodiscard]] constexpr bool has_quirk(Quirk flag) const noexcept {
        return (active_quirks_ & flag) != Quirk::None;
    }

private:
    Quirk active_quirks_{Quirk::None};

    static constexpr std::array<QuirkEntry, 3> Registry{{
        { 0x1000, Quirk::I2cBusyLock | Quirk::UartDmaCorrupt }, // Rev A0
        { 0x1001, Quirk::UartDmaCorrupt },                      // Rev A1
        { 0x2000, Quirk::None }                                 // Rev B0 (Fixed)
    }};
};

} // namespace hardware
