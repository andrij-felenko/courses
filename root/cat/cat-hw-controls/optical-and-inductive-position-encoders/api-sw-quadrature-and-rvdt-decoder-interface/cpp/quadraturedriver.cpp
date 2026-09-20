class QuadratureDriver {
public:
    struct Config {
        uint32_t sampleRateHz;
        uint8_t filterDepth;
        bool enableZIndex;
    };

    bool init(const Config& cfg) {
        position_ = 0;
        errors_ = 0;
        return true;
    }

private:
    volatile int32_t position_{0};
    uint32_t errors_{0};
};
