#ifndef LM35_FILTER_HPP
#define LM35_FILTER_HPP

#include <cstdint>
#include <cstddef>
#include <array>
#include "adc_config.hpp"

/// Тип функціонального вказівника для зчитування аналогового входу мікроконтролера
using AnalogReadCallback = uint16_t(*)(uint8_t pin);

/**
 * @brief Клас LM35Filter для об'єктно-орієнтованої обробки даних давача LM35DZ.
 * 
 * Забезпечує налаштування опорної напруги АЦП (1,1 В), програмне придушення
 * високочастотного шуму за допомогою кільцевого буфера цифрового усереднення
 * та конвертацію напруги в температуру (°C) з калібруванням.
 */
class LM35Filter {
public:
    /// Максимальний розмір кільцевого буфера цифрового усереднення
    static constexpr size_t MAX_BUFFER_CAPACITY = 16;
    /// Коефіцієнт передачі LM35DZ: 10 мВ / °C (0.010 В / °C)
    static constexpr float LM35_SENSITIVITY_V_PER_C = 0.010f;

    /**
     * @brief Конструктор об'єкта драйвера LM35Filter.
     * @param adc_cfg Конфігурація АЦП (опорна напруга 1,1 В, роздільна здатність, аналоговий пин).
     * @param cal_params Калібрувальні коефіцієнти (зсув та масштаб).
     * @param read_cb Зворотний виклик для читання аналогового сигналу.
     * @param window_size Розмір вікна цифрового усереднення (за замовчуванням 8 відліків).
     */
    LM35Filter(AdcConfig adc_cfg,
               CalibrationParams cal_params,
               AnalogReadCallback read_cb,
               size_t window_size = 8) noexcept;

    /**
     * @brief Ініціалізація давача та первинне наповнення буфера усереднення.
     * @return true у разі успішної ініціалізації аналогового тракту.
     */
    bool init() noexcept;

    /**
     * @brief Зчитування нового сирого значення з АЦП та додавання до кільцевого буфера.
     * @return Зчитане сире значення АЦП.
     */
    uint16_t sample() noexcept;

    /**
     * @brief Отримання усередненого значення відліку АЦП з кільцевого буфера.
     */
    float getFilteredRaw() const noexcept;

    /**
     * @brief Розрахунок поточної усередненої температури у градусах Цельсія з урахуванням калібрування.
     */
    float getTemperatureCelsius() const noexcept;

    /**
     * @brief Конвертація сирого значення АЦП у температуру (°C) без усереднення.
     * @param raw_adc Сире значення з АЦП.
     */
    float rawToCelsius(uint16_t raw_adc) const noexcept;

    /**
     * @brief Конвертація сирого значення АЦП у напругу в мілівольтах (мВ).
     * @param raw_adc Сире значення з АЦП.
     */
    float rawToMillivolts(uint16_t raw_adc) const noexcept;

    /**
     * @brief Оновлення конфігурації АЦП.
     */
    void setAdcConfig(const AdcConfig& cfg) noexcept { adc_config_ = cfg; }

    /**
     * @brief Оновлення параметрів калібрування.
     */
    void setCalibration(const CalibrationParams& cal) noexcept { calibration_ = cal; }

    /**
     * @brief Зміна розміру вікна цифрового усереднення.
     * @param window_size Новий розмір вікна (від 1 до MAX_BUFFER_CAPACITY).
     */
    bool setWindowSize(size_t window_size) noexcept;

    /**
     * @brief Отримання поточної конфігурації АЦП.
     */
    const AdcConfig& adcConfig() const noexcept { return adc_config_; }

    /**
     * @brief Отримання поточних параметрів калібрування.
     */
    const CalibrationParams& calibration() const noexcept { return calibration_; }

    /**
     * @brief Отримання поточного розміру вікна усереднення.
     */
    size_t windowSize() const noexcept { return window_size_; }

    /**
     * @brief Очищення вмісту кільцевого буфера.
     */
    void resetBuffer() noexcept;

private:
    AdcConfig adc_config_;
    CalibrationParams calibration_;
    AnalogReadCallback read_callback_{nullptr};

    std::array<uint16_t, MAX_BUFFER_CAPACITY> buffer_{};
    size_t window_size_{8};
    size_t write_index_{0};
    size_t count_{0};
    uint32_t buffer_sum_{0};
};

#endif // LM35_FILTER_HPP
