#pragma once

#include <cstdint>
#include <cstddef>
#include <utility>
#include <vector>

namespace camera {

// Клас SccbBus реалізує низькорівневий протокол SCCB (Serial Camera Control Bus)
// для конфігурації та читання регістрів сенсора зображення OV3640.
class SccbBus {
public:
    explicit SccbBus(uint8_t device_address = 0x3C);
    ~SccbBus() = default;

    // Ініціалізація апаратної шини SCCB/I2C
    bool init();

    // Запис значення у регістр поточного банку
    bool write_register(uint8_t reg, uint8_t value);

    // Зчитування значення з регістру поточного банку
    bool read_register(uint8_t reg, uint8_t& value);

    // Вибір активного банку регістрів (регістр 0xFF у сенсорі OV3640)
    bool select_bank(uint8_t bank);

    // Запис у регістр з явним вказуванням банку
    bool write_bank_register(uint8_t bank, uint8_t reg, uint8_t value);

    // Читання з регістру з явним вказуванням банку
    bool read_bank_register(uint8_t bank, uint8_t reg, uint8_t& value);

    // Перевірка ідентифікатора сенсора (PID: 0x36, VER: 0x40 -> 0x3640)
    bool verify_sensor_id(uint16_t& sensor_id);

    // Запис послідовності пар (регістр, значення) для вибраного банку
    bool write_register_list(uint8_t bank, const std::vector<std::pair<uint8_t, uint8_t>>& reg_list);

private:
    uint8_t device_address_;
    uint8_t current_bank_{0xFF}; // Неіснуючий початковий банк для примусового вибору
    bool initialized_{false};

    // Внутрішній метод виконання передачі даних по шині I2C/SCCB
    bool i2c_transmit(uint8_t reg, uint8_t val);
    bool i2c_receive(uint8_t reg, uint8_t& val);
};

} // namespace camera
