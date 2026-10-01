#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>
#include "MovingAverageFilter.hpp"

// Адреси сенсорів на шині I2C
constexpr uint8_t AHT20_I2C_ADDR  = 0x38;
constexpr uint8_t BMP280_I2C_ADDR = 0x76;

// Параметри часових затримок та періоду опитування
struct PollingConfig {
    uint32_t poll_interval_ms{1000}; // Період між вимірюваннями (мс)
    uint32_t aht20_delay_ms{80};     // Апаратний час перетворення AHT20 (мс)
    uint32_t bmp280_delay_ms{45};    // Апаратний час перетворення BMP280 (мс)
};

// Необроблені сирі показники сенсорів
struct RawClimateData {
    float temperature_aht20{0.0f};
    float humidity_aht20{0.0f};
    float temperature_bmp280{0.0f};
    float pressure_bmp280{0.0f}; // у Паскалях (Па)
    bool  aht20_valid{false};
    bool  bmp280_valid{false};
};

// Згладжені оброблені кліматичні показники
struct ProcessedClimateData {
    float temperature{0.0f};  // Усереднена температура (°C)
    float humidity{0.0f};     // Згладжена відносна вологість (%)
    float pressure_hpa{0.0f}; // Згладжений тиск у гектопаскалях (гПа)
    bool  data_valid{false};  // Прапорець валідності даних
};

// Упакований телеметричний пакет для надсилання по каналах зв'язку
#pragma pack(push, 1)
struct ClimatePacket {
    uint32_t timestamp_ms{0};   // Системний час (мс)
    float    temperature{0.0f};  // Згладжена температура (°C)
    float    humidity{0.0f};     // Згладжена вологість (%RH)
    float    pressure_hpa{0.0f}; // Згладжений тиск (гПа)
    uint8_t  status_flags{0};    // Прапорці стану (Bit 0: AHT20 OK, Bit 1: BMP280 OK, Bit 2: Filter Full)
    uint16_t checksum{0};        // Контрольна сума CRC16-CCITT

    /**
     * @brief Обчислює контрольні суму CRC16-CCITT для полів пакета.
     */
    uint16_t calculateCRC() const;
};
#pragma pack(pop)

// Стан автомата неблокуючого таймерного опитування
enum class NodeState {
    IDLE,             // Очікування нового інтервалу вимірювання
    TRIGGER_AHT20,    // Відправка команди запуску вимірювання AHT20
    WAIT_AHT20,       // Асинхронне очікування завершення перетворення AHT20
    READ_AHT20,       // Зчитування та розбір байтів AHT20
    TRIGGER_BMP280,   // Запуск примусового вимірювання (forced mode) BMP280
    WAIT_BMP280,      // Асинхронне очікування завершення перетворення BMP280
    READ_BMP280,      // Зчитування даних та калібрувальна компенсація BMP280
    PROCESS_AND_PACK  // Фільтрація вибірок, оновлення показників та створення пакета
};

// Інтерфейс шини I2C для ізоляції драйвера від конкретного апаратного рівня (HAL)
class II2CBus {
public:
    virtual ~II2CBus() = default;

    /**
     * @brief Запис байтів у регістри пристрою I2C.
     */
    virtual bool writeRegisters(uint8_t dev_addr, uint8_t reg, const uint8_t* data, std::size_t len) = 0;

    /**
     * @brief Читання байтів з регістрів пристрою I2C.
     */
    virtual bool readRegisters(uint8_t dev_addr, uint8_t reg, uint8_t* data, std::size_t len) = 0;

    /**
     * @brief Послідовний запис байтів пристрою I2C без вказання адреси регістру.
     */
    virtual bool writeBytes(uint8_t dev_addr, const uint8_t* data, std::size_t len) = 0;

    /**
     * @brief Послідовне читання байтів з пристрою I2C.
     */
    virtual bool readBytes(uint8_t dev_addr, uint8_t* data, std::size_t len) = 0;
};

// Структура зберігання заводських калібрувальних коефіцієнтів BMP280
struct BMP280Calibration {
    uint16_t dig_T1{0};
    int16_t  dig_T2{0};
    int16_t  dig_T3{0};
    uint16_t dig_P1{0};
    int16_t  dig_P2{0};
    int16_t  dig_P3{0};
    int16_t  dig_P4{0};
    int16_t  dig_P5{0};
    int16_t  dig_P6{0};
    int16_t  dig_P7{0};
    int16_t  dig_P8{0};
    int16_t  dig_P9{0};
    int32_t  t_fine{0}; // Необхідний для математичної компенсації тиску
};

/**
 * @brief Клас кліматичного вузла для неблокуючого опитування сенсорів AHT20 та BMP280.
 */
class ClimateNode {
public:
    explicit ClimateNode(II2CBus& i2c_bus, PollingConfig config = PollingConfig{});

    /**
     * @brief Виконує початкову ініціалізацію сенсорів AHT20 та BMP280.
     * @return true якщо принаймні один сенсор готов до роботи.
     */
    bool begin();

    /**
     * @brief Основна функція оновлення автомата станів (неблокуюча).
     * @param current_time_ms Поточний системний час у мілісекундах.
     */
    void update(uint32_t current_time_ms);

    /**
     * @brief Перевіряє наявність нового зформованого пакета телеметрії.
     */
    bool hasNewPacket() const { return new_packet_available_; }

    /**
     * @brief Повертає новий телеметричний пакет та скидає прапорець готовності.
     */
    std::optional<ClimatePacket> getLatestPacket();

    /**
     * @brief Повертає поточні оброблені згладжені дані.
     */
    ProcessedClimateData getProcessedData() const { return processed_data_; }

    /**
     * @brief Повертає поточний стан автомата вимірювань.
     */
    NodeState getState() const { return state_; }

private:
    // Низькорівнева робота з AHT20
    bool initAHT20();
    bool triggerAHT20Measurement();
    bool readAHT20Data(float& temperature, float& humidity);

    // Низькорівнева робота з BMP280
    bool initBMP280();
    bool readBMP280Calibration();
    bool triggerBMP280Measurement();
    bool readBMP280Data(float& temperature, float& pressure_pa);

    // Математична компенсація Bosch для BMP280
    int32_t  compensateTemperatureBMP280(int32_t adc_T);
    uint32_t compensatePressureBMP280(int32_t adc_P);

    II2CBus&      i2c_;
    PollingConfig config_;
    NodeState     state_{NodeState::IDLE};

    uint32_t state_timer_ms_{0};
    uint32_t last_poll_start_ms_{0};

    BMP280Calibration    bmp280_calib_{};
    RawClimateData       raw_data_{};
    ProcessedClimateData processed_data_{};
    ClimatePacket        latest_packet_{};
    bool                 new_packet_available_{false};

    // Фільтри ковзного усереднення з розміром буфера 5 вибірок
    MovingAverageFilter<float, 5> temp_filter_;
    MovingAverageFilter<float, 5> humidity_filter_;
    MovingAverageFilter<float, 5> pressure_filter_;
};
