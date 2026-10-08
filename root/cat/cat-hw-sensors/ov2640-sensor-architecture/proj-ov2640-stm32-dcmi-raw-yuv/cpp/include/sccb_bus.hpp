#ifndef SCCB_BUS_HPP
#define SCCB_BUS_HPP

#include <cstdint>
#include <cstddef>

namespace ov2640 {

/// Перелічувальний тип банків внутрішніх регістрів сенсора OV2640
enum class RegisterBank : uint8_t {
    DSP    = 0x00, // Банк цифрової обробки сигналів (DSP / JPEG / Scaling)
    Sensor = 0x01  // Банк налаштування аналогової матриці (Sensor / AGC / AEC / AWB)
};

/// Статуси виконання операцій на шині SCCB
enum class SccbStatus {
    Ok = 0,
    ErrTimeout,
    ErrNack,
    ErrInvalidParam,
    ErrNotInitialized,
    ErrBusHardware
};

/**
 * @brief Низькорівневий C++ драйвер шини SCCB (Serial Camera Control Bus).
 * Забезпечує читання та запис 8-бітних регістрів OV2640 з кешуванням та автоматичним
 * перемиканням банків пам'яті через системний регістр 0xFF.
 */
class SccbBus {
public:
    explicit SccbBus(uint8_t device_address = 0x30);
    ~SccbBus() = default;

    SccbBus(const SccbBus&) = delete;
    SccbBus& operator=(const SccbBus&) = delete;
    SccbBus(SccbBus&&) noexcept = default;
    SccbBus& operator=(SccbBus&&) noexcept = default;

    /// Ініціалізація апаратної периферії I2C/SCCB
    SccbStatus init();

    /// Явний вибір активного банку регістрів (DSP: 0x00, Sensor: 0x01)
    SccbStatus selectBank(RegisterBank bank);

    /// Запис значення в 8-бітний регістр
    SccbStatus writeRegister(uint8_t reg, uint8_t value);

    /// Читання значення з 8-бітного регістра
    SccbStatus readRegister(uint8_t reg, uint8_t& out_value);

    /// Послідовний запис масиву пар {регістр, значення}
    SccbStatus writeRegisterList(const uint8_t reg_pairs[][2], size_t count);

    /// Перевірка ідентифікаційних регістрів пристрою (PID та VER)
    SccbStatus verifyDeviceId(uint8_t& out_pid, uint8_t& out_ver);

    /// Отримання поточного обраного банку
    RegisterBank currentBank() const { return current_bank_; }

    /// Отримання адреси пристрою на шині
    uint8_t deviceAddress() const { return device_address_; }

private:
    uint8_t device_address_;
    RegisterBank current_bank_{RegisterBank::DSP};
    bool is_initialized_{false};

    SccbStatus lowLevelWrite(uint8_t reg, uint8_t val);
    SccbStatus lowLevelRead(uint8_t reg, uint8_t& val);
};

} // namespace ov2640

#endif // SCCB_BUS_HPP
