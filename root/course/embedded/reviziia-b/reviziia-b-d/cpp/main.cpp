#include <cstdint>
#include <array>
#include <optional>
#include <span>

enum class HardwareRevision : uint8_t {
    Unknown = 0,
    RevA    = 1,
    RevB    = 2,
    RevC    = 3
};

struct RevisionWindow {
    HardwareRevision revision;
    uint16_t min_raw;
    uint16_t max_raw;

    [[nodiscard]] constexpr bool contains(uint16_t sample) const noexcept {
        return sample >= min_raw && sample <= max_raw;
    }
};

class BoardSupportPackage {
public:
    static constexpr std::array<RevisionWindow, 3> Windows{{
        { HardwareRevision::RevA,    0,  300 },  // 0.00 В (GND)
        { HardwareRevision::RevB,  850, 1200 },  // 0.825 В
        { HardwareRevision::RevC, 1850, 2250 }   // 1.650 В
    }};

    [[nodiscard]] static HardwareRevision identify(std::span<const uint16_t> adc_samples) noexcept {
        if (adc_samples.empty()) {
            return HardwareRevision::Unknown;
        }

        uint32_t sum = 0;
        for (const auto val : adc_samples) {
            sum += val;
        }
        const auto average = static_cast<uint16_t>(sum / adc_samples.size());

        for (const auto& win : Windows) {
            if (win.contains(average)) {
                return win.revision;
            }
        }
        return HardwareRevision::Unknown;
    }
};
