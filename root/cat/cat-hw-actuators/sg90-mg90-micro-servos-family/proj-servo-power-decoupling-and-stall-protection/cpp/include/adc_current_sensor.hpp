#ifndef ADC_CURRENT_SENSOR_HPP
#define ADC_CURRENT_SENSOR_HPP

#include <cstdint>
#include <cstddef>
#include <array>

namespace towerpro {

/**
 * @brief Налаштування АЦП та датчика струму живлення сервоприводу.
 */
struct AdcSensorConfig {
    uint8_t adcPin{0};                ///< Номер аналогового виводу АЦП
    float referenceVoltageV{3.3f};    ///< Опорна напруга АЦП (В)
    uint16_t adcResolution{4096};     ///< Роздільна здатність АЦП (12 біт = 4096)
    float shuntResistanceOhm{0.05f};  ///< Опір вимірювального шунта (Ом)
    float ampGain{20.0f};             ///< Коефіцієнт підсилення струмового підсилювача
    float zeroCurrentOffsetV{0.0f};   ///< Напруга зміщення нульового струму (В)
    uint32_t sampleIntervalUs{1000};  ///< Інтервал вибірок АЦП у мікросекундах (1 мс)
};

/**
 * @brief Клас неблокуючого АЦП-вимірювача струму з цифровою фільтрацією.
 * 
 * Здійснює накопичення вибірок та згладжування методом ковзного середнього (Moving Average)
 * для усунення імпульсних завад від колекторного двигуна та перетворення сирих значень АЦП у мА.
 */
class AdcCurrentSensor {
public:
    static constexpr size_t FILTER_WINDOW_SIZE = 16;

    AdcCurrentSensor() = default;

    /**
     * @brief Ініціалізація вимірювача струму.
     * @param config Параметри АЦП та вимірювального кола.
     * @return true у разі коректних параметрів.
     */
    bool begin(const AdcSensorConfig& config);

    /**
     * @brief Неблокуюче оновлення вибірок струму.
     * @param currentMicros Поточний системний час у мікросекундах.
     */
    void update(uint32_t currentMicros);

    /**
     * @brief Отримати відфільтроване значення струму в міліамперах.
     */
    float readCurrentmA() const;

    /**
     * @brief Отримати поточну напругу на виході вимірювача (В).
     */
    float getRawVoltage() const;

    /**
     * @brief Встановити симульоване значення АЦП для тестування.
     */
    void setSimulatedRawAdc(uint16_t rawAdcValue);

    /**
     * @brief Очистити буфер ковзного середнього.
     */
    void resetFilter();

private:
    AdcSensorConfig config_{};
    std::array<float, FILTER_WINDOW_SIZE> sampleBuffer_{};
    size_t bufferIndex_{0};
    size_t sampleCount_{0};
    float accumulatedSum_{0.0f};
    float filteredCurrentmA_{0.0f};
    uint32_t lastSampleMicros_{0};

    uint16_t simulatedRawAdc_{0};
    bool simulatedMode_{false};

    float rawAdcToCurrentmA(uint16_t adcVal) const;
};

} // namespace towerpro

#endif // ADC_CURRENT_SENSOR_HPP
