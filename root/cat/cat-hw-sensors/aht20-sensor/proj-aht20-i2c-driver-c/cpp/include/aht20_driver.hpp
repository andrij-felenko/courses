#pragma once

#include <cstddef>
#include <cstdint>
#include <chrono>
#include <memory>
#include <string>

namespace aht20 {

/// Стандартна I2C-адреса давача AHT20
constexpr uint8_t DEFAULT_I2C_ADDR = 0x38;

/// Статуси виконання операцій драйвера AHT20
enum class Aht20Status {
    Success = 0,
    ErrI2cTransfer,
    ErrNotCalibrated,
    ErrTimeout,
    ErrCrcMismatch,
    ErrDeviceBusy
};

/// Структура зчитаних кліматичних параметрів
struct Aht20Data {
    float temperature_c = 0.0f;  ///< Температура в градусах Цельсія
    float humidity_rh = 0.0f;    ///< Відносна вологість у відсотках (%RH)
    bool valid = false;          ///< Прапорець достовірності даних
};

/**
 * @brief RAII-обгортка для безпечного керування транзакціями та станом шини I2C.
 * Гарантує закриття файлового дескриптора або звільнення ресурсу шини при виході з області видимості.
 */
class I2cBusGuard {
public:
    explicit I2cBusGuard(const std::string& device_path, uint8_t address, bool mock_mode = false);
    ~I2cBusGuard();

    I2cBusGuard(const I2cBusGuard&) = delete;
    I2cBusGuard& operator=(const I2cBusGuard&) = delete;

    I2cBusGuard(I2cBusGuard&& other) noexcept;
    I2cBusGuard& operator=(I2cBusGuard&& other) noexcept;

    /**
     * @brief Записує послідовність байтів на шину I2C.
     */
    bool write_bytes(const uint8_t* data, size_t length);

    /**
     * @brief Зчитує послідовність байтів із шини I2C.
     */
    bool read_bytes(uint8_t* buffer, size_t length);

    /**
     * @brief Перевіряє стан готовності інтерфейсу I2C.
     */
    bool is_valid() const noexcept { return fd_ >= 0 || mock_mode_; }

    /**
     * @brief Перевіряє, чи активний режим симуляції.
     */
    bool is_mock() const noexcept { return mock_mode_; }

private:
    void close_bus() noexcept;

    int fd_ = -1;
    uint8_t address_ = DEFAULT_I2C_ADDR;
    bool mock_mode_ = false;
    std::string dev_path_;

    // Симуляційні поля для mock-режиму
    uint8_t mock_status_ = 0x08; // Статус за замовчуванням: calibrated, non-busy
    bool mock_measuring_ = false;
};

/**
 * @brief Об'єктно-орієнтований драйвер для цифрового давача температури та вологості AHT20.
 * Підтримує RAII-ініціалізацію, моніторинг статусних прапорців та перевірку CRC8.
 */
class Aht20Driver {
public:
    static constexpr uint8_t CMD_INIT[3] = {0xBE, 0x08, 0x00};
    static constexpr uint8_t CMD_MEASURE[3] = {0xAC, 0x33, 0x00};
    static constexpr uint8_t CMD_SOFT_RESET = 0xBA;

    static constexpr uint8_t STATUS_BUSY_MASK = 0x80;
    static constexpr uint8_t STATUS_CALIBRATED_MASK = 0x08;

    /**
     * @brief Конструктор драйвера. Застосовує RAII для автоматичної ініціалізації пристрою.
     * @param i2c_path Шлях до файлу пристрою I2C (наприклад, /dev/i2c-1).
     * @param address I2C-адреса давача (за замовчуванням 0x38).
     * @param mock_mode Режим симуляції (для тестування без апаратного забезпечення).
     */
    explicit Aht20Driver(const std::string& i2c_path = "/dev/i2c-1",
                        uint8_t address = DEFAULT_I2C_ADDR,
                        bool mock_mode = false);

    ~Aht20Driver() = default;

    /**
     * @brief Виконує перевірку калібрування та ініціалізацію давача AHT20.
     * @return Aht20Status Результат виконання ініціалізації.
     */
    Aht20Status initialize();

    /**
     * @brief Зчитує поточний байт статусу AHT20.
     * @param out_status Посилання для збереження зчитаного байта статусу.
     */
    Aht20Status read_status_byte(uint8_t& out_status);

    /**
     * @brief Запускає процес вимірювання (надсилає команду 0xAC, 0x33, 0x00).
     */
    Aht20Status trigger_measurement();

    /**
     * @brief Очікує завершення вимірювання, зчитує 7-байтовий кадр і перевіряє CRC8.
     * @param out_data Посилання на структуру для збереження результатів.
     * @param timeout Граничний час очікування готовності даних.
     */
    Aht20Status read_measurement(Aht20Data& out_data,
                                 std::chrono::milliseconds timeout = std::chrono::milliseconds(150));

    /**
     * @brief Зручний метод full-cycle: запускає вимірювання, очікує потрібну затримку та зчитує дані.
     * @param out_data Посилання на структуру для збереження результатів.
     */
    Aht20Status read_sample(Aht20Data& out_data);

    /**
     * @brief Перезавантажує внутрішню логіку давача (команда Soft Reset 0xBA).
     */
    Aht20Status soft_reset();

    /**
     * @brief Математично розпаковує 20-бітні сирі значення температури й вологості.
     * @param frame 7-байтовий масив кадру AHT20.
     * @param out_temp Перетворене значення температури в °C.
     * @param out_humidity Перетворене значення вологості в %RH.
     */
    static void parse_raw_data(const uint8_t frame[7], float& out_temp, float& out_humidity) noexcept;

private:
    I2cBusGuard bus_;
    bool is_initialized_ = false;
};

} // namespace aht20
