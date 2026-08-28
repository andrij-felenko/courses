#include <cstdint>
#include <array>
#include <expected>
#include <span>
#include <algorithm>
#include <cmath>
#include <iostream>

namespace sensors::bme280 {

struct CalibrationData {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
    uint8_t  dig_H1;
    int16_t  dig_H2;
    uint8_t  dig_H3;
    int16_t  dig_H4;
    int16_t  dig_H5;
    int8_t   dig_H6;
};

struct SensorReadings {
    double temperature_celsius;
    double relative_humidity_pct;
};

enum class DriverError {
    I2CReadFailure,
    I2CWriteFailure,
    InvalidDeviceID
};

class BME280Driver {
public:
    explicit BME280Driver(uint8_t i2c_addr = 0x76) : i2c_address_(i2c_addr) {}

    // Ініціалізація шини та зчитування NVM коефіцієнтів
    [[nodiscard]] std::expected<void, DriverError> initialize() {
        uint8_t id = read_register(0xD0);
        if (id != 0x60) {
            return std::unexpected(DriverError::InvalidDeviceID);
        }

        // Зчитування таблиць компенсації температури й вологості
        calib_.dig_T1 = read_u16_le(0x88);
        calib_.dig_T2 = read_s16_le(0x8A);
        calib_.dig_T3 = read_s16_le(0x8C);
        
        calib_.dig_H1 = read_register(0xA1);
        calib_.dig_H2 = read_s16_le(0xE1);
        calib_.dig_H3 = read_register(0xE3);
        
        uint8_t e4 = read_register(0xE4);
        uint8_t e5 = read_register(0xE5);
        uint8_t e6 = read_register(0xE6);
        calib_.dig_H4 = static_cast<int16_t>((e4 << 4) | (e5 & 0x0F));
        calib_.dig_H5 = static_cast<int16_t>((e6 << 4) | (e5 >> 4));
        calib_.dig_H6 = static_cast<int8_t>(read_register(0xE7));

        // Налаштування режимів: Humidity x1, Temp x1, Normal Mode
        write_register(0xF2, 0x01); // ctrl_hum
        write_register(0xF4, 0x27); // ctrl_meas

        return {};
    }

    // Повний цикл розрахунку замірів
    [[nodiscard]] std::expected<SensorReadings, DriverError> read_data() const {
        std::array<uint8_t, 8> raw_buf{};
        if (!read_burst(0xF7, raw_buf)) {
            return std::unexpected(DriverError::I2CReadFailure);
        }

        int32_t adc_T = (raw_buf[3] << 12) | (raw_buf[4] << 4) | (raw_buf[5] >> 4);
        int32_t adc_H = (raw_buf[6] << 8) | raw_buf[7];

        // 1. Обчислення t_fine
        int32_t var1_t = ((((adc_T >> 3) - (static_cast<int32_t>(calib_.dig_T1) << 1))) * static_cast<int32_t>(calib_.dig_T2)) >> 11;
        int32_t var2_t = (((((adc_T >> 4) - static_cast<int32_t>(calib_.dig_T1)) * ((adc_T >> 4) - static_cast<int32_t>(calib_.dig_T1))) >> 12) * static_cast<int32_t>(calib_.dig_T3)) >> 14;
        int32_t t_fine = var1_t + var2_t;
        double temp = ((t_fine * 5 + 128) >> 8) / 100.0;

        // 2. Обчислення вологості
        int32_t v_x1 = (t_fine - 76800);
        v_x1 = (((((adc_H << 14) - (static_cast<int32_t>(calib_.dig_H4) << 20) - (static_cast<int32_t>(calib_.dig_H5) * v_x1)) + 16384) >> 15) *
                (((((((v_x1 * static_cast<int32_t>(calib_.dig_H6)) >> 10) * (((v_x1 * static_cast<int32_t>(calib_.dig_H3)) >> 11) + 32768)) >> 10) + 2097152) *
                  static_cast<int32_t>(calib_.dig_H2) + 8192) >> 14));
        v_x1 = (v_x1 - (((((v_x1 >> 15) * (v_x1 >> 15)) >> 7) * static_cast<int32_t>(calib_.dig_H1)) >> 4));
        v_x1 = std::clamp(v_x1, 0, 419430400);
        double humidity = (v_x1 >> 12) / 1024.0;

        return SensorReadings{temp, humidity};
    }

private:
    uint8_t i2c_address_;
    CalibrationData calib_{};

    uint8_t read_register(uint8_t reg) const { return (reg == 0xD0) ? 0x60 : 0; }
    uint16_t read_u16_le(uint8_t reg) const { return 27504; }
    int16_t read_s16_le(uint8_t reg) const { return 26435; }
    void write_register(uint8_t reg, uint8_t val) const {}
    bool read_burst(uint8_t reg, std::span<uint8_t> out) const {
        std::fill(out.begin(), out.end(), 0x80);
        return true;
    }
};

} // namespace sensors::bme280

int main() {
    sensors::bme280::BME280Driver sensor(0x76);
    if (sensor.initialize()) {
        auto readings = sensor.read_data();
        if (readings) {
            std::cout << "BME280 C++ Driver: T = " << readings->temperature_celsius 
                      << " C, RH = " << readings->relative_humidity_pct << " %\n";
        }
    }
    return 0;
}
