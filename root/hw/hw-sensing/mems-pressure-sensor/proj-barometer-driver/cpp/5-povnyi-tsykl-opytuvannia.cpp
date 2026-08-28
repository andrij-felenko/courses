namespace app {

// Концепт шини I2C для статичного поліморфізму без віртуальних таблиць
template <typename T>
concept I2cInterface = requires(T bus, uint8_t addr, uint8_t reg, std::span<uint8_t> buf) {
    { bus.read_bytes(addr, reg, buf.data(), buf.size()) } -> std::same_as<bool>;
};

template <I2cInterface I2cBus>
class BarometerTask {
private:
    I2cBus& bus_;
    uint8_t i2c_addr_{0x76};
    drivers::BaroCalibCoeffs calib_{};
    drivers::AltimeterFilter filter_{0.15, 101325.0};

public:
    explicit BarometerTask(I2cBus& bus, uint8_t addr = 0x76) noexcept
        : bus_(bus), i2c_addr_(addr) {}

    std::expected<void, drivers::BaroError> init() noexcept {
        uint8_t nvm_buf[21];
        if (!bus_.read_bytes(i2c_addr_, 0x31, nvm_buf, sizeof(nvm_buf))) {
            return std::unexpected(drivers::BaroError::CommunicationFailure);
        }
        calib_ = drivers::MemsBarometerParser::parse_calibration(nvm_buf);
        return {};
    }

    std::expected<drivers::BaroSample, drivers::BaroError> update() noexcept {
        uint8_t raw_buf[6];
        if (!bus_.read_bytes(i2c_addr_, 0x04, raw_buf, sizeof(raw_buf))) {
            return std::unexpected(drivers::BaroError::CommunicationFailure);
        }

        const uint32_t raw_p = static_cast<uint32_t>(raw_buf[0]) |
                              (static_cast<uint32_t>(raw_buf[1]) << 8) |
                              (static_cast<uint32_t>(raw_buf[2]) << 16);

        const uint32_t raw_t = static_cast<uint32_t>(raw_buf[3]) |
                              (static_cast<uint32_t>(raw_buf[4]) << 8) |
                              (static_cast<uint32_t>(raw_buf[5]) << 16);

        const double t_c = drivers::BaroCompensator::compensate_temperature(calib_, raw_t);
        const double p_pa = drivers::BaroCompensator::compensate_pressure(calib_, raw_p, t_c);

        return filter_.process(p_pa, t_c);
    }
};

} // namespace app
