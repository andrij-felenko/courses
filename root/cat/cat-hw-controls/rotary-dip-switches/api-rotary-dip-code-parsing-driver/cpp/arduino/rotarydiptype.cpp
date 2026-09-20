#include <cstdint>
#include <array>

enum class RotaryDipType : uint8_t {
    BcdDirect = 0,
    BcdComplementary,
    HexDirect,
    HexComplementary,
    GrayCode
};

struct RotaryDipConfig {
    std::array<int8_t, 4> pins; // Виводи розрядів 1, 2, 4, 8
    RotaryDipType type = RotaryDipType::HexDirect;
    bool activeLow = true;
    uint16_t debounceMs = 20;
};

class RotaryDipDriver {
public:
    bool begin(const RotaryDipConfig& config);
    uint8_t decodeRawCode(uint8_t rawCode) const;
};
