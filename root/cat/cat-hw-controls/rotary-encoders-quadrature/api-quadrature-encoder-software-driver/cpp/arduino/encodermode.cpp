#include <cstdint>

enum class EncoderMode : uint8_t {
    Mode1X = 1,
    Mode2X = 2,
    Mode4X = 4
};

struct EncoderConfig {
    int8_t pinA;
    int8_t pinB;
    int8_t pinButton;
    uint32_t ppr;
    EncoderMode mode = EncoderMode::Mode4X;
    bool invertDirection = false;
    int32_t minPosition = INT32_MIN;
    int32_t maxPosition = INT32_MAX;
    uint16_t buttonDebounceMs = 50;
    bool enableIndexPin = false;
};

class EncoderDriver {
public:
    bool begin(const EncoderConfig& config);
};
