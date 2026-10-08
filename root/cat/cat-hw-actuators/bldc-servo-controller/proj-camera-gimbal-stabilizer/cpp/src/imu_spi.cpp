#include "imu_spi.hpp"
#include <cmath>
#include <algorithm>

namespace gimbal {

static constexpr float DEG_TO_RAD = 0.017453292519943295f;
static constexpr float GRAVITY_EARTH = 9.80665f;

bool SpiImuHandler::init(const ImuConfig& config) {
    config_ = config;

    // Встановлення лінії CS в активний високий стан (деактивовано)
    deselect_cs();

    // Перевірка зв'язку з датчиком через регістр WHO_AM_I
    uint8_t who_am_i = 0;
    read_registers(REG_WHO_AM_I, &who_am_i, 1);

    if (who_am_i != WHO_AM_I_RESPONSE && who_am_i != 0x70 && who_am_i != 0x73) {
        // Якщо ідентифікатор не збігається, проводиться м'яке скидання та спроба
        write_register(REG_PWR_MGMT_1, 0x80); // Reset command
        who_am_i = 0;
        read_registers(REG_WHO_AM_I, &who_am_i, 1);
    }

    // Вивід IMU із режимів сну (Power Management: Clock Select Auto)
    write_register(REG_PWR_MGMT_1, 0x01);

    initialized_ = true;
    accumulated_angle_ = 0.0f;
    last_update_us_ = 0;
    return initialized_;
}

void SpiImuHandler::select_cs() {
    // Емуляція/виклики низькорівневого контролю піна CS (Low)
}

void SpiImuHandler::deselect_cs() {
    // Емуляція/виклики низькорівневого контролю піна CS (High)
}

uint8_t SpiImuHandler::spi_transfer_byte(uint8_t data) {
    // Низькорівневий обмін байтом через шину SPI
    return data;
}

void SpiImuHandler::read_registers(uint8_t reg_addr, uint8_t* buffer, size_t length) {
    select_cs();
    // Прапор читання SPI (MSB = 1)
    spi_transfer_byte(reg_addr | 0x80);
    for (size_t i = 0; i < length; ++i) {
        buffer[i] = spi_transfer_byte(0x00);
    }
    deselect_cs();
}

void SpiImuHandler::write_register(uint8_t reg_addr, uint8_t value) {
    select_cs();
    // Прапор запису SPI (MSB = 0)
    spi_transfer_byte(reg_addr & 0x7F);
    spi_transfer_byte(value);
    deselect_cs();
}

bool SpiImuHandler::read_sensor(ImuData& out_data) {
    if (!initialized_) {
        out_data.valid = false;
        return false;
    }

    // Пакетне зчитування 14 байт: Акселерометр (6B) + Температура (2B) + Гіроскоп (6B)
    uint8_t raw_buffer[14]{0};
    read_registers(REG_ACCEL_XOUT_H, raw_buffer, sizeof(raw_buffer));

    // Розпакування 16-бітних значень із доповненням до двох (Big Endian)
    int16_t raw_accel_x = static_cast<int16_t>((raw_buffer[0] << 8) | raw_buffer[1]);
    int16_t raw_accel_y = static_cast<int16_t>((raw_buffer[2] << 8) | raw_buffer[3]);
    int16_t raw_accel_z = static_cast<int16_t>((raw_buffer[4] << 8) | raw_buffer[5]);

    int16_t raw_gyro_z  = static_cast<int16_t>((raw_buffer[12] << 8) | raw_buffer[13]);

    // Масштабування первинних вимірювань у фізичні одиниці
    float gyro_dps = static_cast<float>(raw_gyro_z) / config_.gyro_lsb_per_dps;
    out_data.gyro_rad_s = gyro_dps * DEG_TO_RAD;

    out_data.accel_m_s2[0] = (static_cast<float>(raw_accel_x) / config_.accel_lsb_per_g) * GRAVITY_EARTH;
    out_data.accel_m_s2[1] = (static_cast<float>(raw_accel_y) / config_.accel_lsb_per_g) * GRAVITY_EARTH;
    out_data.accel_m_s2[2] = (static_cast<float>(raw_accel_z) / config_.accel_lsb_per_g) * GRAVITY_EARTH;

    // Розрахунок кута нахилу за акселерометром та чисельне інтегрування швидкості
    float accel_angle = std::atan2(out_data.accel_m_s2[1], out_data.accel_m_s2[2]);

    // Комплементарна фільтрація кута для об'єднання акселерометра та гіроскопа
    constexpr float dt = 0.001f; // 1 кГц дискретизація
    constexpr float alpha = 0.98f;
    accumulated_angle_ = alpha * (accumulated_angle_ + out_data.gyro_rad_s * dt) + (1.0f - alpha) * accel_angle;

    out_data.angle_rad = accumulated_angle_;
    out_data.timestamp_us += 1000;
    out_data.valid = true;

    return true;
}

} // namespace gimbal
