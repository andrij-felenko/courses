#ifndef BLHELI_ESC_HPP
#define BLHELI_ESC_HPP

#include <cstdint>

/**
 * @brief Клас для керування безколекторним регулятором ходу (ESC) BLHeli 30A.
 * 
 * Забезпечує генерацію ШІМ-сигналу серво-типу (1000..2000 мкс), автоматичне
 * калібрування крайніх точок газу під час старту та постійний моніторинг
 * напруги вбудованого BEC (Battery Eliminator Circuit) через АЦП.
 */
class BLHeliESC {
public:
    // Константи тривалості ШІМ-імпульсів (у мікросекундах)
    static constexpr uint16_t MIN_PULSE_US = 1000;   ///< Мінімальний імпульс (0% газу / стоп)
    static constexpr uint16_t MAX_PULSE_US = 2000;   ///< Максимальний імпульс (100% газу)
    static constexpr uint16_t SAFE_PULSE_US = 1000;  ///< Безпечний імпульс при аварійній зупинці

    // Параметри вимірювання напруги BEC через АЦП
    static constexpr float ADC_REF_VOLTAGE = 3.3f;        ///< Опорна напруга АЦП мікроконтролера (В)
    static constexpr uint16_t ADC_MAX_RAW = 4095;         ///< 12-бітна роздільна здатність АЦП (2^12 - 1)
    static constexpr float BEC_SAFE_VOLTAGE_MIN = 4.75f; ///< Мінімальна безпечна напруга BEC (В)

    /**
     * @brief Конструктор класу BLHeliESC
     * @param pwm_pin Номер виводу (піна) для виходу ШІМ-сигналу керування
     * @param adc_pin Номер аналогового виводу (АЦП) для моніторингу лінії BEC
     * @param voltage_divider_ratio Коефіцієнт дільника напруги BEC (за замовчуванням 2.0f)
     */
    BLHeliESC(uint8_t pwm_pin, uint8_t adc_pin, float voltage_divider_ratio = 2.0f);

    /**
     * @brief Ініціалізація периферійних модулів (таймера ШІМ та АЦП)
     * @return true у разі успішної ініціалізації
     */
    bool init();

    /**
     * @brief Виконання автокалібрування крайніх точок газу (Max/Min Throttle)
     * 
     * Алгоритм передає максимальний імпульс (2000 мкс) під час підключення живлення ESC,
     * очікує звукових сигналів підтвердження від ESC, після чого знижує сигнал до 1000 мкс.
     */
    void calibrate();

    /**
     * @brief Встановлення рівня газу у відсотках (0.0% .. 100.0%)
     * @param percent Значення газу у відсотках
     */
    void setThrottlePercent(float percent);

    /**
     * @brief Встановлення тривалості імпульсу газу в мікросекундах
     * @param pulse_us Тривалість імпульсу (обмежується діапазоном 1000..2000 мкс)
     */
    void setPulseWidthUs(uint16_t pulse_us);

    /**
     * @brief Отримання поточної встановленої тривалості імпульсу
     * @return Тривалість імпульсу у мікросекундах
     */
    uint16_t getPulseWidthUs() const;

    /**
     * @brief Зчитування поточної реальної напруги BEC через АЦП
     * @return Обчислена напруга BEC у Вольтах
     */
    float readBECVoltage();

    /**
     * @brief Перевірка стабільності та безпеки живлення BEC
     * @return true, якщо напруга BEC знаходиться в межах норми
     */
    bool isBECVoltageSafe();

    /**
     * @brief Аварійна зупинка мотора (скидання газу в 0)
     */
    void emergencyStop();

    /**
     * @brief Перевірка стану проходження калібрування
     * @return true, якщо ESC відкалібровано
     */
    bool isCalibrated() const;

private:
    uint8_t pwm_pin_;             ///< Пін генерації ШІМ
    uint8_t adc_pin_;             ///< Пін АЦП моніторингу
    uint16_t current_pulse_us_;   ///< Поточна тривалість імпульсу (мкс)
    float divider_ratio_;         ///< Коефіціент дільника напруги
    bool is_calibrated_;          ///< Статус виконання калібрування

    // Низькорівневі допоміжні методи для роботи з апаратурою
    void hw_set_pwm_us(uint16_t us);
    uint16_t hw_read_adc_raw();
    void hw_delay_ms(uint32_t ms);
};

#endif // BLHELI_ESC_HPP
