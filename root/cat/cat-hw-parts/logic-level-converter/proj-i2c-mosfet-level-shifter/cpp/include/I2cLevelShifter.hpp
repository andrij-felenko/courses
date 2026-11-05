#pragma once

#include <cstdint>
#include <cstddef>
#include <system_error>

namespace hardware {

/**
 * @brief Перелік швидкостей шини I2C з урахуванням ємності навантаження
 *        через MOSFET-транзисторний перетворювач рівнів.
 */
enum class BusSpeed : uint32_t {
    Standard = 100000, // 100 кГц (стандартний режим, повільніші фронти через високий опір підтяжки)
    Fast = 400000      // 400 кГц (швидкий режим, вимагає менших номіналів підтягувальних резисторів)
};

/**
 * @brief Перелік помилок обміну даними через транслятор рівнів.
 */
enum class I2cError {
    Success = 0,
    Nack,          // Отримано NACK від периферії (можлива проблема живлення або адреси)
    Timeout,       // Тайм-аут арбітражу або очікування лінії SCL/SDA
    BusBusy,       // Лінія I2C залишається притиснутою донизу (зависання MOSFET)
    InvalidParam   // Некоректні параметри конфігурації
};

/**
 * @brief Клас для керування апаратним I2C контролером через MOSFET-транслятор рівнів (BSS138).
 */
class I2cLevelShifter {
public:
    /**
     * @brief Конструктор ініціалізації шини I2C.
     * @param port Номер апаратного порту I2C (наприклад, 0 або 1).
     * @param sda_pin Номер виводу SDA.
     * @param scl_pin Номер виводу SCL.
     * @param speed Початкова швидкість шини.
     */
    explicit I2cLevelShifter(int port, int sda_pin, int scl_pin, BusSpeed speed = BusSpeed::Standard) noexcept;

    // Заборона копіювання для збереження апаратного ресурсу (RAII)
    I2cLevelShifter(const I2cLevelShifter&) = delete;
    I2cLevelShifter& operator=(const I2cLevelShifter&) = delete;

    // Дозволяємо перенесення
    I2cLevelShifter(I2cLevelShifter&& other) noexcept;
    I2cLevelShifter& operator=(I2cLevelShifter&& other) noexcept;

    /**
     * @brief Деструктор: коректно звільняє ресурси драйвера I2C.
     */
    ~I2cLevelShifter() noexcept;

    /**
     * @brief Зміна швидкості шини "на льоту" з урахуванням затримок транзистора.
     */
    I2cError setSpeed(BusSpeed speed) noexcept;

    /**
     * @brief Запис байтів до 5В пристрою через транслятор.
     */
    I2cError writeData(uint8_t device_address, const uint8_t* data, size_t length) noexcept;

    /**
     * @brief Читання байтів з 5В пристрою через транслятор рівнів.
     */
    I2cError readData(uint8_t device_address, uint8_t* buffer, size_t length) noexcept;

    /**
     * @brief Програмне відновлення шини у випадку зависання MOSFET (Clock Recovery / Bus Clear).
     */
    I2cError recoverBus() noexcept;

private:
    int port_;
    int sda_pin_;
    int scl_pin_;
    BusSpeed speed_;
    bool initialized_;
};

} // namespace hardware
