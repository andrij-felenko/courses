#include <cstdint>
#include <array>

enum class ThumbwheelCodeType {
    BcdDirect = 0,
    BcdComplement,
    Hexadecimal
};

struct ThumbwheelConfig {
    uint8_t numDecades;
    ThumbwheelCodeType codeType;
    bool activeLow;
    uint8_t debounceTicks;
    const uint8_t *scanPins;
    const uint8_t *dataPins;
};

struct DecadeState {
    uint8_t rawCode{0xFF};
    uint8_t candidateCode{0xFF};
    uint8_t debouncedCode{0xFF};
    uint8_t stabilityCounter{0};
    bool isValid{false};
};

class ThumbwheelDriver {
public:
    explicit ThumbwheelDriver(const ThumbwheelConfig &config) : config_(config) {}
    void init();
    void scanTick();
    bool readValue(uint32_t &outValue) const;

private:
    const ThumbwheelConfig &config_;
    std::array<DecadeState, 8> decades_{};
    uint32_t validatedValue_{0};
    bool hasError_{false};
};
