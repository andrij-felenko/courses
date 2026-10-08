#ifndef MAX31865_SENSOR_HPP
#define MAX31865_SENSOR_HPP

#include <cstdint>
#include <cstddef>
#include <functional>
#include <optional>
#include <array>

/**
 * @brief Тип платинового термометра опору (RTD).
 */
enum class RtdType : uint8_t {
    PT100 = 0,   // Опір при 0 °C дорівнює 100 Ом
    PT1000 = 1   // Опір при 0 °C дорівнює 1000 Ом
};

/**
 * @brief Схема підключення датчика RTD (кількість дротів).
 */
enum class WireMode : uint8_t {
    TwoWire = 0,   // 2-дротова або 4-дротова схема
    ThreeWire = 1, // 3-дротова схема компенсації опору ліній
    FourWire = 0   // 4-дротова схема (налаштування регістра тотожне 2-дротовій)
};

/**
 * @brief Частота вбудованого режекторного фільтра перешкод.
 */
enum class FilterFrequency : uint8_t {
    Hz60 = 0, // Пригнічення наводок 60 Гц
    Hz50 = 1  // Пригнічення наводок 50 Гц
};

/**
 * @brief Стани скінченного автомата (FSM) неблокуючого драйвера MAX31865.
 */
enum class SensorState : uint8_t {
    Uninitialized,   // Драйвер не ініціалізовано
    Idle,            // Режим очікування між вимірюваннями
    BiasStabilizing, // Очікування стабілізації опорної напруги VBIAS (10 мс)
    Converting,      // Виконується АЦП-перетворення (очікування сигналу DRDY)
    DataReady,       // Дані готові до зчитання
    FaultDetected    // Виявлено апаратну несправність
};

/**
 * @brief Конфігураційні параметри для налаштування MAX31865 та RTD.
 */
struct RtdConfig {
    RtdType type{RtdType::PT100};
    WireMode wire_mode{WireMode::ThreeWire};
    FilterFrequency filter{FilterFrequency::Hz50};
    float r_ref_ohm{400.0f};             // Опорний опір Rref (400 Ом для PT100, 4000 Ом для PT1000)
    float r_0_ohm{100.0f};               // Номінальний опір RTD при 0 °C (100 Ом або 1000 Ом)
    float lower_temp_limit{-200.0f};     // Нижня допустима межа температури (°C)
    float upper_temp_limit{850.0f};      // Верхня допустима межа температури (°C)
    uint16_t high_threshold_adc{0x7FFF}; // Верхня межа коду АЦП для виклику тривоги
    uint16_t low_threshold_adc{0x0000};  // Нижня межа коду АЦП для виклику тривоги
};

/**
 * @brief Прапорці апаратної діагностики регістра помилок MAX31865 (адреса 0x07).
 */
struct FaultFlags {
    bool high_threshold_exceeded{false};     // Біт 7: Вихід за верхній поріг температури/опору
    bool low_threshold_exceeded{false};      // Біт 6: Вихід за нижній поріг температури/опору
    bool refin_greater_than_085_vbias{false};// Біт 5: REFIN- > 0.85 * VBIAS (обрив FORCE- / коротке на VBIAS)
    bool refin_less_than_085_vbias{false};   // Біт 4: REFIN- < 0.85 * VBIAS (обрив FORCE- / коротке на GND)
    bool rtdin_less_than_085_vbias{false};   // Біт 3: RTDIN- < 0.85 * VBIAS (обрив RTDIN- / коротке на GND)
    bool over_under_voltage{false};          // Біт 2: Перенапруга або знижена напруга на виводах
    uint8_t raw_byte{0};                     // Сирий байт регістра 0x07

    [[nodiscard]] bool anyFault() const noexcept {
        return (raw_byte & 0xFC) != 0;
    }
};

/**
 * @brief Структура підсумкової телеметрії вимірювальної системи.
 */
struct RtdTelemetry {
    float temperature_c{0.0f};      // Обчислена температура в градусах Цельсія
    float resistance_ohm{0.0f};     // Виміряний опір терморезистора в Омах
    uint16_t raw_adc{0};            // 15-бітний сухий код АЦП
    FaultFlags fault{};             // Прапорці діагностики несправностей
    bool is_valid{false};           // Ознака коректності даних
    uint32_t timestamp_ms{0};       // Системна мітка часу вимірювання (мс)
};

// Типи зворотних викликів для апаратної абстракції SPI та системного часу
using SpiTransferFn = std::function<bool(const uint8_t* tx_data, uint8_t* rx_data, size_t length)>;
using GpioWriteFn = std::function<void(bool state)>;
using GetTickMsFn = std::function<uint32_t()>;

class MAX31865Sensor;

/**
 * @brief RAII-обгортка для автоматичного відстеження апаратних несправностей,
 * безпечного скидання прапорців у регістрі конфігурації та захисту стану вимірювальної системи.
 */
class RtdFaultGuard {
public:
    explicit RtdFaultGuard(MAX31865Sensor& sensor);
    ~RtdFaultGuard();

    RtdFaultGuard(const RtdFaultGuard&) = delete;
    RtdFaultGuard& operator=(const RtdFaultGuard&) = delete;

    RtdFaultGuard(RtdFaultGuard&& other) noexcept;
    RtdFaultGuard& operator=(RtdFaultGuard&& other) noexcept;

    [[nodiscard]] bool hasFault() const noexcept { return cached_fault_.anyFault(); }
    [[nodiscard]] FaultFlags flags() const noexcept { return cached_fault_; }

    void clearAndReset();
    void release() noexcept { active_ = false; }

private:
    MAX31865Sensor* sensor_{nullptr};
    FaultFlags cached_fault_{};
    bool active_{false};
};

/**
 * @brief C++ клас драйвера перетворювача опору MAX31865.
 * Реалізує асинхронне неблокуюче опитування АЦП через SPI та обробку переривань EXTI DRDY.
 */
class MAX31865Sensor {
public:
    // Адреси регістрів MAX31865
    static constexpr uint8_t REG_CONFIG         = 0x00;
    static constexpr uint8_t REG_RTD_MSB        = 0x01;
    static constexpr uint8_t REG_RTD_LSB        = 0x02;
    static constexpr uint8_t REG_HIGH_FAULT_MSB = 0x03;
    static constexpr uint8_t REG_HIGH_FAULT_LSB = 0x04;
    static constexpr uint8_t REG_LOW_FAULT_MSB  = 0x05;
    static constexpr uint8_t REG_LOW_FAULT_LSB  = 0x06;
    static constexpr uint8_t REG_FAULT_STATUS   = 0x07;

    // Біти регістра конфігурації 0x00
    static constexpr uint8_t CONFIG_VBIAS       = (1 << 7);
    static constexpr uint8_t CONFIG_MODE_AUTO   = (1 << 6);
    static constexpr uint8_t CONFIG_1SHOT       = (1 << 5);
    static constexpr uint8_t CONFIG_3WIRE       = (1 << 4);
    static constexpr uint8_t CONFIG_FAULT_CLEAR = (1 << 1);
    static constexpr uint8_t CONFIG_FILTER_50HZ  = (1 << 0);

    MAX31865Sensor(SpiTransferFn spi_transfer, GpioWriteFn cs_write, GetTickMsFn get_tick_ms);

    /**
     * @brief Ініціалізація мікросхеми MAX31865 та початкова конфігурація регістрів.
     */
    bool begin(const RtdConfig& config);

    /**
     * @brief Запуск асинхронного одиночного перетворення АЦП (1-Shot mode).
     */
    bool startAsyncConversion();

    /**
     * @brief Обробник зовнішнього переривання EXTI для лінії DRDY (готовність даних).
     */
    void handleExtiInterrupt() noexcept;

    /**
     * @brief Оновлення скінченного автомата (FSM). Викликається в головному циклі програми.
     */
    void processFsm();

    /**
     * @brief Зчитати поточний регістр помилок (0x07).
     */
    FaultFlags readFaultRegister();

    /**
     * @brief Скидання прапорців помилок у конфігураційному регістрі MAX31865.
     */
    bool clearFaultRegister();

    [[nodiscard]] SensorState state() const noexcept { return state_; }
    [[nodiscard]] std::optional<RtdTelemetry> getLatestTelemetry() const noexcept;
    [[nodiscard]] const RtdConfig& config() const noexcept { return config_; }

private:
    uint8_t readRegister(uint8_t reg);
    bool writeRegister(uint8_t reg, uint8_t value);
    bool readRegisters(uint8_t start_reg, uint8_t* buffer, size_t length);

    SpiTransferFn spi_transfer_;
    GpioWriteFn cs_write_;
    GetTickMsFn get_tick_ms_;

    RtdConfig config_{};
    SensorState state_{SensorState::Uninitialized};
    volatile bool drdy_pending_{false};
    uint32_t bias_start_ticks_{0};
    uint32_t conversion_start_ticks_{0};

    RtdTelemetry latest_telemetry_{};
};

#endif // MAX31865_SENSOR_HPP
