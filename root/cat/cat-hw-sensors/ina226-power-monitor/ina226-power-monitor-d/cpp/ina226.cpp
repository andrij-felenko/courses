// Покрокове обчислення та запис регістру калібрування INA226 по I2C на C++
#include <cstdint>
#include <cmath>
#include <array>
#include <cstddef>

class Ina226 {
public:
    static constexpr uint8_t REG_CALIBRATION = 0x05;

    // Низькорівневий інтерфейс запису I2C для конкретної платформи
    virtual bool i2c_write(uint8_t dev_addr, const uint8_t* data, std::size_t length) = 0;

    // Обчислення коефіцієнта калібрування з перевіркою переповнення
    static constexpr uint16_t calculate_cal(double r_shunt_ohms, double current_lsb_amps) noexcept {
        const double cal_raw = 0.00512 / (current_lsb_amps * r_shunt_ohms);
        return (cal_raw > 65535.0) ? 65535 : static_cast<uint16_t>(cal_raw);
    }

    // Покрокове обчислення та трансляція пакету в шину I2C
    bool set_calibration(uint8_t dev_addr, double r_shunt_ohms, double current_lsb_amps) {
        const double cal_raw = 0.00512 / (current_lsb_amps * r_shunt_ohms);
        if (cal_raw > 65535.0) {
            return false; // Помилка: значення не вміщується у 16 біт
        }

        const uint16_t cal_val = static_cast<uint16_t>(std::floor(cal_raw));
        const std::array<uint8_t, 3> packet = {
            REG_CALIBRATION,
            static_cast<uint8_t>((cal_val >> 8) & 0xFF), // MSB
            static_cast<uint8_t>(cal_val & 0xFF)         // LSB
        };

        return i2c_write(dev_addr, packet.data(), packet.size());
    }
};
