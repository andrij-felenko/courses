#include <cstdint>

enum class ThumbwheelStatus : int8_t {
    Ok          =  0,
    InvalidBcd  = -1,
    Busy        = -2
};

struct ThumbwheelConfig {
    uint8_t pinPl;
    uint8_t pinClk;
    uint8_t pinData;
    uint8_t decadesCount;
    bool activeLowLogic;
};

class ThumbwheelDriver {
public:
    ThumbwheelStatus init(const ThumbwheelConfig& config);
    ThumbwheelStatus poll();
    uint16_t getValue() const { return validatedValue_; }

private:
    ThumbwheelConfig config_;
    uint16_t rawLatch_{0};
    uint8_t nibbles_[4]{0};
    uint8_t debounceCnt_[4]{0};
    uint8_t prevNibbles_[4]{0};
    uint16_t validatedValue_{0};
};
