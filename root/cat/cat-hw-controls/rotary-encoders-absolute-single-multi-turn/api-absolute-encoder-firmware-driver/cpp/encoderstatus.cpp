enum class EncoderStatus : uint8_t {
    Ok,
    Timeout,
    CrcError,
    HardwareFault,
    LowBattery
};

class EncoderDriver {
public:
    [[nodiscard]] EncoderStatus processFrame(uint64_t rawFrame, EncoderData& data) const noexcept {
        bool errBit = (rawFrame >> 1) & 1;
        bool warnBit = rawFrame & 1;

        if (!errBit) {
            data.error_flag = true;
            return EncoderStatus::HardwareFault;
        }
        data.warning_flag = !warnBit;
        return EncoderStatus::Ok;
    }
};
