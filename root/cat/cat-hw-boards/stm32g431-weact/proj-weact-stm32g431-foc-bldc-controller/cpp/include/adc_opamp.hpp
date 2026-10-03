#ifndef ADC_OPAMP_HPP
#define ADC_OPAMP_HPP

#include <cstdint>

#if __has_include("stm32g4xx.h")
#include "stm32g4xx.h"
#endif

namespace foc {

/**
 * @brief Драйвер аналогового тракту (OPAMP + ADC1/ADC2) для вимірювання фазних струмів.
 * Інкапсулює роботу вбудованих операційних підсилювачів та синхронне оцифрування АЦП.
 */
class AdcOpampDriver {
public:
    /**
     * @brief Конструктор аналогового драйвера.
     * @param current_scale Коефіцієнт масштабування (Ампер на одиницю АЦП).
     */
    explicit AdcOpampDriver(float current_scale = 0.01f);

    /**
     * @brief Ініціалізація перифериферійних блоків OPAMP1, OPAMP2, ADC1, ADC2 та переривань.
     * @return true якщо ініціалізація успішна.
     */
    bool init();

    /**
     * @brief Виконання автокалібрування зсуву нуля (Zero-Current Offset calibration).
     * @param num_samples Кількість вибірок для усереднення.
     */
    void calibrateOffsets(uint16_t num_samples = 1024);

    /**
     * @brief Зчитування останніх сирих значень оцифрування АЦП.
     * @param raw_a Вихідний параметр для фази A.
     * @param raw_b Вихідний параметр для фази B.
     */
    void readRawSamples(uint16_t& raw_a, uint16_t& raw_b);

    /**
     * @brief Отримання відкаліброваних значення фазних струмів в Амперах.
     * @param i_a Вихідний струм фази A (Ампери).
     * @param i_b Вихідний струм фази B (Ампери).
     */
    void getPhaseCurrents(float& i_a, float& i_b);

    /**
     * @brief Перевірка статусу автокалібрування.
     */
    bool isCalibrated() const { return calibrated_; }

    /**
     * @brief Отримання обчисленого зсуву нуля фази A.
     */
    float getOffsetA() const { return offset_a_; }

    /**
     * @brief Отримання обчисленого зсуву нуля фази B.
     */
    float getOffsetB() const { return offset_b_; }

private:
    float current_scale_;
    float offset_a_{2048.0f};
    float offset_b_{2048.0f};
    uint16_t raw_adc_a_{0};
    uint16_t raw_adc_b_{0};
    bool calibrated_{false};

    void configureOPAMP();
    void configureADC();
};

} // namespace foc

#endif // ADC_OPAMP_HPP
