#include "vl53l0x_sensor.hpp"

namespace tof {

Vl53l0xSensor::Vl53l0xSensor(std::size_t id, int xshut_pin, int interrupt_pin, II2cBus& i2c_bus, IGpioController& gpio)
    : sensor_id_(id),
      xshut_pin_(xshut_pin),
      interrupt_pin_(interrupt_pin),
      i2c_bus_(i2c_bus),
      gpio_(gpio) {
    gpio_.set_pin_mode_output(xshut_pin_);
    gpio_.set_pin_mode_input_pullup(interrupt_pin_);
}

void Vl53l0xSensor::hardware_power_off() {
    gpio_.write_pin(xshut_pin_, false);
}

void Vl53l0xSensor::hardware_power_on() {
    gpio_.write_pin(xshut_pin_, true);
}

bool Vl53l0xSensor::set_i2c_address(uint8_t new_address) {
    // Вхідне значення звужується до 7-бітної адреси I2C
    uint8_t addr7bit = new_address & 0x7F;
    if (!write_reg(REG_I2C_SLAVE_DEVICE_ADDRESS, addr7bit)) {
        return false;
    }
    current_address_ = addr7bit;
    return true;
}

bool Vl53l0xSensor::initialize() {
    // Перевірка ідентифікатора пристрою VL53L0X (очікується 0xEE)
    uint8_t model_id = 0;
    if (!read_reg(REG_IDENTIFICATION_MODEL_ID, model_id) || model_id != 0xEE) {
        return false;
    }

    // Налаштування конфігурації апаратного переривання GPIO1:
    // значення 0x04 визначає активний низький рівень (active-low) при готовності нових даних
    if (!write_reg(REG_SYSTEM_INTERRUPT_CONFIG_GPIO, 0x04)) {
        return false;
    }

    // Скидання наявного прапорця переривання
    clear_interrupt();
    return true;
}

bool Vl53l0xSensor::start_continuous() {
    // Запис 0x02 у REG_SYSRANGE_START вмикає режим циклічного вимірювання (back-to-back continuous mode)
    if (!write_reg(REG_SYSRANGE_START, 0x02)) {
        return false;
    }
    is_continuous_ = true;
    return true;
}

bool Vl53l0xSensor::stop_continuous() {
    // Запис 0x01 зупиняє циклічне вимірювання
    if (!write_reg(REG_SYSRANGE_START, 0x01)) {
        return false;
    }
    is_continuous_ = false;
    return true;
}

bool Vl53l0xSensor::is_data_ready() {
    // Спершу перевіряємо апаратну лінію переривання (активний низький рівень GPIO1)
    if (!gpio_.read_pin(interrupt_pin_)) {
        return true;
    }

    // Якщо апаратна лінія висока, перевіряємо регістр статусу переривань
    uint8_t status = 0;
    if (read_reg(REG_RESULT_INTERRUPT_STATUS, status)) {
        return (status & 0x07) != 0;
    }
    return false;
}

std::optional<MeasurementResult> Vl53l0xSensor::read_range_continuous() {
    uint8_t raw_status = 0;
    if (!read_reg(REG_RESULT_RANGE_STATUS, raw_status)) {
        return std::nullopt;
    }

    // Відстань у міліметрах зберігається як 16-бітне число зсувом +10 байтів від REG_RESULT_RANGE_STATUS
    uint16_t raw_mm = 0;
    if (!read_reg16(REG_RESULT_RANGE_STATUS + 10, raw_mm)) {
        return std::nullopt;
    }

    MeasurementResult result;
    result.distance_mm = raw_mm;
    // Біти 3..6 містять код статусу вимірювання (0 — вимірювання успішне)
    result.range_status = (raw_status >> 3) & 0x0F;
    result.is_valid = (result.range_status == 0);

    return result;
}

bool Vl53l0xSensor::clear_interrupt() {
    // Запис 0x01 у REG_SYSTEM_INTERRUPT_CLEAR очищує апаратний прапор переривання VL53L0X
    return write_reg(REG_SYSTEM_INTERRUPT_CLEAR, 0x01);
}

bool Vl53l0xSensor::write_reg(uint8_t reg, uint8_t val) {
    return i2c_bus_.write_register(current_address_, reg, val);
}

bool Vl53l0xSensor::write_reg16(uint8_t reg, uint16_t val) {
    return i2c_bus_.write_register16(current_address_, reg, val);
}

bool Vl53l0xSensor::read_reg(uint8_t reg, uint8_t& val) {
    return i2c_bus_.read_register(current_address_, reg, val);
}

bool Vl53l0xSensor::read_reg16(uint8_t reg, uint16_t& val) {
    return i2c_bus_.read_register16(current_address_, reg, val);
}

} // namespace tof
