#ifndef AHT20_HPP
#define AHT20_HPP

#include <cstdint>
#include <cstddef>

// Абстрактний інтерфейс шини I2C для апаратної незалежності
class I2CBus {
public:
    virtual ~I2CBus() = default;

    // Запис даних на шину I2C за вказаною адресою
    virtual bool write(uint8_t address, const uint8_t* data, std::size_t length) = 0;

    // Читання даних з шини I2C за вказаною адресою
    virtual bool read(uint8_t address, uint8_t* data, std::size_t length) = 0;
};

// Стан драйвера давача AHT20
enum class DriverState {
    Uninitialized, // Драйвер не ініціалізовано
    Idle,          // Готовий до запуску нових вимірювань
    Measuring,     // Триває процес асинхронного вимірювання
    Error          // Виникла помилка під час обміну або обробки
};

// Коди помилок драйвера
enum class ErrorCode {
    None,          // Помилок немає
    BusError,      // Помилка введення-виведення на шині I2C
    NotCalibrated, // Давач не відкалібрований
    Timeout,       // Давач перебуває в стані зайнятості занадто довго
    CrcMismatch    // Контрольна сума CRC-8 не збігається
};

// Структура для збереження результатів вимірювання
struct Measurement {
    float temperature{0.0f}; // Температура у градусах Цельсія
    float humidity{0.0f};    // Відносна вологість у відсотках
    bool isValid{false};     // Ознака коректності отриманих даних
};

// Клас драйвера давача температури та вологості AHT20
class AHT20 {
public:
    static constexpr uint8_t DEFAULT_ADDRESS = 0x38;
    static constexpr uint32_t MEASUREMENT_DELAY_MS = 80;

    explicit AHT20(I2CBus& bus, uint8_t address = DEFAULT_ADDRESS);

    // Ініціалізація та перевірка стану давача
    bool reset();

    // Запуск асинхронного вимірювання
    bool startMeasurement(uint32_t currentTimeMs);

    // Оновлення автомата станів (неблокуюче опитування за таймером)
    bool update(uint32_t currentTimeMs);

    // Отримання останнього збереженого результату
    Measurement getMeasurement() const;

    // Отримання поточного стану драйвера
    DriverState getState() const;

    // Отримання останнього коду помилки
    ErrorCode getLastError() const;

    // Обчислення контрольної суми CRC-8 (поліном 0x31, початковий стан 0xFF)
    static uint8_t calculateCRC8(const uint8_t* data, std::size_t length);

private:
    static constexpr uint8_t CMD_INIT = 0xBE;
    static constexpr uint8_t CMD_MEASURE = 0xAC;
    static constexpr uint8_t STATUS_BUSY_MASK = 0x80;
    static constexpr uint8_t STATUS_CALIBRATED_MASK = 0x08;

    bool readStatus(uint8_t& status);

    I2CBus& bus_;
    uint8_t address_;
    DriverState state_{DriverState::Uninitialized};
    ErrorCode lastError_{ErrorCode::None};
    Measurement lastMeasurement_{};
    uint32_t measurementStartTimeMs_{0};
};

#endif // AHT20_HPP
