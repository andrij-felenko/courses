namespace link_api {

struct ArbiterConfig {
    uint8_t  failoverPerThresh{25};
    int16_t  failoverRssiThresh{-95};
    uint8_t  lossBurstLimit{4};

    uint8_t  recoveryPerThresh{5};
    uint16_t recoveryDwellMs{5000};
    uint16_t recoveryPacketStreak{50};

    uint16_t heartbeatTimeoutMs{3000};
    bool     enableRfSwitchGpio{true};
    uint8_t  rfSwitchGpioPin{12};
};

} // namespace link_api
