enum class MotorStatus {
    Ok = 0,
    InvalidArg,
    PwmInitFailed
};

struct MotorConfig {
    uint8_t pinPwm;
    uint8_t pinDir1;
    uint8_t pinDir2;
    uint8_t pinCurrent;
    uint32_t pwmFreqHz{20000};
};

class MotorDriver {
public:
    MotorStatus init(const MotorConfig& cfg);
};
