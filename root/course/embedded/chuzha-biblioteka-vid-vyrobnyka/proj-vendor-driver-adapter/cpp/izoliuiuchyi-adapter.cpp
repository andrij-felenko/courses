class SensorAdapter {
public:
    SensorAdapter(II2cBus& bus, uint8_t i2c_addr)
        : bus_(bus), i2c_addr_(i2c_addr) {
        vendor_dev_.intf_ptr = this;
        vendor_dev_.read = c_read_bridge;
        vendor_dev_.write = c_write_bridge;
        vendor_dev_.delay_us = c_delay_bridge;
    }

    ~SensorAdapter() {
        if (initialized_) {
            /* Безпечний перевід сенсора у режим сну (RAII) */
            uint8_t sleep_cmd = 0x00;
            vendor_dev_.write(0xF4, &sleep_cmd, 1, this);
        }
    }

    /* Заборона копіювання для уникнення розсинхронізації вказівника intf_ptr */
    SensorAdapter(const SensorAdapter&) = delete;
    SensorAdapter& operator=(const SensorAdapter&) = delete;

    SensorAdapter(SensorAdapter&&) noexcept = default;
    SensorAdapter& operator=(SensorAdapter&&) noexcept = default;

    std::expected<void, SensorStatus> init() {
        uint8_t chip_id = 0;
        if (vendor_dev_.read(0xD0, &chip_id, 1, this) != 0) {
            return std::unexpected(SensorStatus::CommunicationError);
        }
        if (chip_id != 0x58 && chip_id != 0x60) {
            return std::unexpected(SensorStatus::InvalidDevice);
        }
        vendor_dev_.chip_id = chip_id;
        initialized_ = true;
        return {};
    }

    std::expected<EnvironmentReading, SensorStatus> read_sample() {
        if (!initialized_) {
            return std::unexpected(SensorStatus::InvalidParameter);
        }

        uint8_t raw_buffer[6] = {0};
        if (vendor_dev_.read(0xF7, raw_buffer, sizeof(raw_buffer), this) != 0) {
            return std::unexpected(SensorStatus::CommunicationError);
        }

        /* Вендорські розрахунки компенсації (симуляція розбору) */
        int32_t raw_press = (int32_t)((((uint32_t)raw_buffer[0]) << 12) |
                                      (((uint32_t)raw_buffer[1]) << 4) |
                                      ((uint32_t)raw_buffer[2] >> 4));
        int32_t raw_temp  = (int32_t)((((uint32_t)raw_buffer[3]) << 12) |
                                      (((uint32_t)raw_buffer[4]) << 4) |
                                      ((uint32_t)raw_buffer[5] >> 4));

        EnvironmentReading reading{};
        reading.temperature_celsius = static_cast<float>(raw_temp) / 100.0f;
        reading.pressure_hpa = static_cast<float>(raw_press) / 100.0f;
        return reading;
    }

private:
    static int8_t c_read_bridge(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr) {
        if (!intf_ptr || !data || len == 0) return -1;
        auto* self = static_cast<SensorAdapter*>(intf_ptr);
        std::span<uint8_t> buf(data, len);
        return self->bus_.read_registers(self->i2c_addr_, reg_addr, buf) ? 0 : -2;
    }

    static int8_t c_write_bridge(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr) {
        if (!intf_ptr || !data || len == 0) return -1;
        auto* self = static_cast<SensorAdapter*>(intf_ptr);
        std::span<const uint8_t> buf(data, len);
        return self->bus_.write_registers(self->i2c_addr_, reg_addr, buf) ? 0 : -2;
    }

    static void c_delay_bridge(uint32_t period_us, void *intf_ptr) {
        (void)intf_ptr;
        /* У виробничому коді: vTaskDelay(pdMS_TO_TICKS(period_us / 1000)) */
    }

    II2cBus& bus_;
    uint8_t i2c_addr_;
    vendor_sensor_dev_t vendor_dev_{};
    bool initialized_{false};
};
