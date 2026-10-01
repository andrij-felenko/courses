class Pt100Driver {
public:
    enum class Status {
        Ok = 0,
        CommunicationError,
        InvalidParam,
        HardwareFault
    };

    Status init(const Pt100Config& config) {
        if (config.r_ref_ohms <= 0.0f) {
            return Status::InvalidParam;
        }

        uint8_t chip_id = 0;
        if (!readRegister(0x00, chip_id) || chip_id != 0x80) {
            return Status::CommunicationError;
        }

        uint8_t conf_reg = (config.wire_mode == Pt100WireMode::ThreeWire) ? 0x10 : 0x00;
        if (!writeRegister(0x01, conf_reg)) {
            return Status::HardwareFault;
        }

        config_ = config;
        is_initialized_ = true;
        return Status::Ok;
    }

private:
    Pt100Config config_;
    bool is_initialized_{false};
    bool readRegister(uint8_t reg, uint8_t& val);
    bool writeRegister(uint8_t reg, uint8_t val);
};
