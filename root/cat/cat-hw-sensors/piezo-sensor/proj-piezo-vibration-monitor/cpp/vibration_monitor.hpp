#ifndef VIBRATION_MONITOR_HPP
#define VIBRATION_MONITOR_HPP

#include <cstdint>

/**
 * @brief Конфігурація пікового фільтра огинаючої вібраційного сигналу.
 */
struct PeakFilterConfig {
    float decay_factor;     ///< Коефіцієнт згасання пікового огинача (0.0f .. 1.0f)
    uint16_t noise_floor;   ///< Поріг відсікання шуму АЦП (відліки нижче цього значення вважаються 0)
};

/**
 * @brief Конфігурація порогів та затримок захисного реле.
 */
struct RelayProtectionConfig {
    uint16_t alarm_threshold;    ///< Поріг спрацьовування тривоги (амплітуда АЦП)
    uint16_t recovery_threshold; ///< Поріг відновлення (гістерезис, recovery_threshold < alarm_threshold)
    uint32_t trip_delay_ms;      ///< Затримка підтвердження тривоги в мс (захист від коротких сплесків)
    uint32_t recovery_delay_ms;  ///< Затримка повернення в безпечний стан після зниження вібрації в мс
};

/**
 * @brief Стани скінченного автомата (FSM) захисного реле.
 */
enum class RelayState : uint8_t {
    NORMAL,         ///< Нормальний стан: вібрація в нормі, реле вимкнено
    TRIP_DELAY,     ///< Очікування спрацьовування: перевищено поріг, відлік затримки
    ALARM,          ///< Аварійний стан: реле активовано, виявлено небезпечну вібрацію
    RECOVERY_DELAY  ///< Очікування відновлення: рівень впав нижче гістерезису, очікування стабілізації
};

/**
 * @brief Клас монітора вібрації для обробки сигналів п'єзоелектричного давача.
 */
class VibrationMonitor {
public:
    VibrationMonitor(const PeakFilterConfig& filter_cfg, const RelayProtectionConfig& relay_cfg);

    /**
     * @brief Обробка нового відліку АЦП та оновлення стану скінченного автомата.
     * @param raw_adc_value Сирий відлік з аналогового входу АЦП
     * @param current_time_ms Поточний час системи у мілісекундах
     */
    void update(uint16_t raw_adc_value, uint32_t current_time_ms);

    /**
     * @brief Отримати поточну амплітуду огинаючої вібрації.
     */
    float getPeakEnvelope() const;

    /**
     * @brief Отримати поточний стан автомата захисного реле.
     */
    RelayState getRelayState() const;

    /**
     * @brief Перевірити, чи активовано захисне реле (аварія).
     */
    bool isRelayActive() const;

    /**
     * @brief Скидання стану монітора в початкове значення.
     */
    void reset(uint32_t current_time_ms);

private:
    PeakFilterConfig filter_cfg_;
    RelayProtectionConfig relay_cfg_;

    float peak_envelope_;
    RelayState state_;
    uint32_t state_timer_ms_;

    void processPeakFilter(uint16_t raw_adc_value);
    void updateFSM(uint32_t current_time_ms);
};

#endif // VIBRATION_MONITOR_HPP
