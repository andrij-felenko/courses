#pragma once

#include <cstdint>
#include <cstddef>

namespace gimbal {

/// @brief Структура для збереження фізичних даних телеметрії з IMU-датчика
struct ImuData {
    float angle_rad{0.0f};       ///< Поточний кут орієнтації (рад)
    float gyro_rad_s{0.0f};      ///< Поточна кутова швидкість (рад/с)
    float accel_m_s2[3]{0.0f, 0.0f, 0.0f}; ///< Лінійні прискорення по XYZ (м/с²)
    uint32_t timestamp_us{0};    ///< Метка часу зчитування в мікросекундах
    bool valid{false};           ///< Прапор придатності даних
};

/// @brief Конфігураційні параметри SPI-інтерфейсу IMU
struct ImuConfig {
    uint8_t cs_pin{10};          ///< Номер піна Chip Select
    uint32_t spi_speed_hz{8000000}; ///< Частота шини SPI (8 МГц)
    float gyro_lsb_per_dps{16.4f};  ///< Чутливість гіроскопа (LSB / (градус/с))
    float accel_lsb_per_g{2048.0f}; ///< Чутливість акселерометра (LSB / g)
};

/// @brief Клас для обробки даних IMU через SPI-інтерфейс у режимі реального часу
class SpiImuHandler {
public:
    SpiImuHandler() = default;
    ~SpiImuHandler() = default;

    /// @brief Ініціалізація шини SPI та налаштування регістрів IMU
    /// @param config Конфігурація CS-піна та масштабування датчика
    /// @return true у разі успішного з'єднання та валідації WHO_AM_I
    bool init(const ImuConfig& config);

    /// @brief Зчитування первинних регістрів та перетворення у фізичні величини
    /// @param out_data Посилання на структуру для збереження результатів
    /// @return true якщо зчитування успішне та КС коректна
    bool read_sensor(ImuData& out_data);

    /// @brief Перевірка статусу працездатності датчика
    bool is_ready() const { return initialized_; }

private:
    /// @brief Низькорівневе керування лінією Chip Select
    void select_cs();
    void deselect_cs();

    /// @brief Передача та прийом одного байта через SPI
    uint8_t spi_transfer_byte(uint8_t data);

    /// @brief Пакетне зчитування регістрів починаючи з reg_addr
    void read_registers(uint8_t reg_addr, uint8_t* buffer, size_t length);

    /// @brief Запис значення в конкретний регістр датчика
    void write_register(uint8_t reg_addr, uint8_t value);

    ImuConfig config_{};
    bool initialized_{false};
    float accumulated_angle_{0.0f};
    uint32_t last_update_us_{0};

    // Адреси регістрів IMU (наприклад, сумісних із MPU9250/ICM-20689)
    static constexpr uint8_t REG_WHO_AM_I = 0x75;
    static constexpr uint8_t REG_PWR_MGMT_1 = 0x6B;
    static constexpr uint8_t REG_ACCEL_XOUT_H = 0x3B;
    static constexpr uint8_t REG_GYRO_ZOUT_H = 0x43;
    static constexpr uint8_t WHO_AM_I_RESPONSE = 0x71;
};

} // namespace gimbal
