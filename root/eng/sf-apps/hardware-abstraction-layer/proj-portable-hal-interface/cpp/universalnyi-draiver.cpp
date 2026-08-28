/* ========================================================================= */
/* Шаблонний драйвер датчика BME280 на C++20 над концептом I2cMaster        */
/* ========================================================================= */

namespace sensors {

template <hal::I2cMaster Bus>
class Bme280 {
public:
    static constexpr uint8_t DefaultAddress = 0x76;
    static constexpr uint8_t ChipIdRegister = 0xD0;
    static constexpr uint8_t ExpectedChipId = 0x60;
    static constexpr uint8_t CalibRegister  = 0x88;
    static constexpr uint8_t CtrlMeasReg    = 0xF4;
    static constexpr uint8_t TempMsbReg     = 0xFA;

    struct CalibrationData {
        uint16_t dig_T1{0};
        int16_t  dig_T2{0};
        int16_t  dig_T3{0};
    };

    explicit Bme280(Bus& bus, uint8_t address = DefaultAddress) noexcept
        : bus_(bus), address_(address) {}

    hal::Status init() noexcept {
        /* 1. Перевірка ідентифікатора чипа */
        const std::array<uint8_t, 1> reg_tx{ChipIdRegister};
        std::array<uint8_t, 1> id_rx{0};

        auto status = bus_.write_read(address_, reg_tx, id_rx, 100);
        if (!hal::is_ok(status)) return status;
        if (id_rx[0] != ExpectedChipId) return hal::Status::Error;

        /* 2. Зчитування калібрувальної таблиці */
        const std::array<uint8_t, 1> calib_tx{CalibRegister};
        std::array<uint8_t, 6> calib_rx{};
        status = bus_.write_read(address_, calib_tx, calib_rx, 100);
        if (!hal::is_ok(status)) return status;

        calib_.dig_T1 = static_cast<uint16_t>(calib_rx[0] | (calib_rx[1] << 8));
        calib_.dig_T2 = static_cast<int16_t>(calib_rx[2] | (calib_rx[3] << 8));
        calib_.dig_T3 = static_cast<int16_t>(calib_rx[4] | (calib_rx[5] << 8));

        /* 3. Налаштування вимірювань */
        const std::array<uint8_t, 2> cfg_tx{CtrlMeasReg, (1U << 5) | (1U << 2) | (3U)};
        return bus_.write(address_, cfg_tx, 100);
    }

    [[nodiscard]] std::pair<hal::Status, int32_t> read_temperature_c_x100() noexcept {
        const std::array<uint8_t, 1> reg_tx{TempMsbReg};
        std::array<uint8_t, 3> raw_rx{};

        auto status = bus_.write_read(address_, reg_tx, raw_rx, 100);
        if (!hal::is_ok(status)) return {status, 0};

        int32_t adc_T = static_cast<int32_t>(
            (static_cast<uint32_t>(raw_rx[0]) << 12) |
            (static_cast<uint32_t>(raw_rx[1]) << 4) |
            (static_cast<uint32_t>(raw_rx[2]) >> 4)
        );

        int32_t var1 = ((((adc_T >> 3) - (static_cast<int32_t>(calib_.dig_T1) << 1))) *
                        static_cast<int32_t>(calib_.dig_T2)) >> 11;
        int32_t var2 = (((((adc_T >> 4) - static_cast<int32_t>(calib_.dig_T1)) *
                          ((adc_T >> 4) - static_cast<int32_t>(calib_.dig_T1))) >> 12) *
                        static_cast<int32_t>(calib_.dig_T3)) >> 14;

        int32_t t_fine = var1 + var2;
        int32_t temp_c_x100 = (t_fine * 5 + 128) >> 8;
        return {hal::Status::Ok, temp_c_x100};
    }

private:
    Bus& bus_;
    uint8_t address_;
    CalibrationData calib_{};
};

} // namespace sensors
