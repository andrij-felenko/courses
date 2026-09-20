#pragma once

#include <stdint.h>
#include <stddef.h>

/**
 * @brief Перелік можливих станів та помилок декодера галетного перемикача.
 */
enum class SelectorStatus : uint8_t {
    OK = 0,               ///< Позицію успішно визначено в межах норми
    DEBOUNCING,           ///< Відбувається часова фільтрація брязкоту
    FAULT_OPEN_CIRCUIT,   ///< Аварійний стан: АЦП показує обрив лінії (близько VCC)
    FAULT_SHORT_CIRCUIT   ///< Аварійний стан: АЦП показує коротке замикання (близько 0V)
};

/**
 * @brief Структура опису події зміни стану селектора.
 */
struct SelectorEvent {
    uint8_t position;        ///< Вибрана позиція (1..12, або 0 при помилці)
    uint16_t rawAdc;         ///< Відфільтроване значення АЦП
    SelectorStatus status;   ///< Поточний статус декодера
};

/**
 * @brief Клас-декодер 12-позиційного аналогового галетного перемикача.
 */
class RotarySelector {
public:
    /// Тип обробника подій зміни позиції (сигнатури void(const SelectorEvent&))
    typedef void (*EventCallback)(const SelectorEvent& event);

    /**
     * @brief Конструктор декодера.
     * @param adcPin Номер аналогового піна АЦП
     * @param debounceMs Час фільтрації брязкоту в мілісекундах (за замовчуванням 30 мс)
     */
    explicit RotarySelector(uint8_t adcPin, uint32_t debounceMs = 30);

    /**
     * @brief Налаштування обробника подій.
     * @param callback Функція зворотного виклику
     */
    void setCallback(EventCallback callback);

    /**
     * @brief Неблокуючий метод оновлення стану декодера (викликається в loop).
     * @param currentMs Поточний час у мілісекундах
     * @param rawAdcValue Сире значення з АЦП (0..4095 або 0..1023)
     */
    void update(uint32_t currentMs, uint16_t rawAdcValue);

    /**
     * @brief Отримати поточну підтверджену позицію (1..12, 0 якщо помилка).
     */
    uint8_t getPosition() const { return m_confirmedPosition; }

    /**
     * @brief Отримати поточний статус роботи декодера.
     */
    SelectorStatus getStatus() const { return m_status; }

private:
    static constexpr uint8_t NUM_POSITIONS = 12;
    static constexpr uint8_t MEDIAN_WINDOW = 5;
    static constexpr uint16_t ADC_MAX_VAL = 4095;
    static constexpr uint16_t HYSTERESIS_ADC = 35;

    uint8_t m_adcPin;
    uint32_t m_debounceMs;
    EventCallback m_callback;

    uint16_t m_filterWindow[MEDIAN_WINDOW];
    uint8_t m_filterIdx;
    bool m_bufferFull;

    uint8_t m_confirmedPosition;
    uint8_t m_pendingPosition;
    uint32_t m_debounceStartTime;
    SelectorStatus m_status;

    uint16_t applyMedianFilter(uint16_t sample);
    uint8_t decodeAdcToPosition(uint16_t adcVal, SelectorStatus& statusOut) const;
};
