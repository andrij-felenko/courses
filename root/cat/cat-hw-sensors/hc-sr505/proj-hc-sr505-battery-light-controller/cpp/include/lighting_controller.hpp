#ifndef LIGHTING_CONTROLLER_HPP
#define LIGHTING_CONTROLLER_HPP

#include <cstdint>
#include "pir_sensor.hpp"

// Передголошення для зменшення зв'язаності
class PowerManager;

/**
 * @brief Стани конечного автомата керування освітленням.
 */
enum class ControllerState : uint8_t {
    Idle,       ///< Очікування руху, світло вимкнено
    LightOn,    ///< Світло увімкнено, рух активний або відраховується таймаут
    Timeout,    ///< Завершення руху, зворотний відлік до вимкнення світла
    Sleep       ///< Перехід мікроконтролера в режим сну
};

/**
 * @brief Контролер неблокуючого керування освітленням на базі HC-SR505.
 * 
 * Реалізує кінцевий автомат, що реагує на події від PirSensor, утримує світло
 * увімкненим протягом заданого часу затримки, перезапускає таймер при повторному русі
 * та передає керування PowerManager для засинання.
 */
class LightingController {
public:
    /**
     * @brief Конструктор контролера освітлення.
     * @param sensor Посилання на об'єкт давача руху PirSensor.
     * @param power_mgr Посилання на об'єкт керування живленням PowerManager.
     * @param relay_pin Номер GPIO виводу для керування реле або силовим ключем.
     * @param hold_duration_ms Час утримання світла увімкненим після зникнення руху (мс).
     */
    LightingController(PirSensor& sensor, PowerManager& power_mgr, uint8_t relay_pin, uint32_t hold_duration_ms);

    /**
     * @brief Ініціалізація периферії контролера (GPIO силового ключа).
     */
    void init();

    /**
     * @brief Основний метод оновлення стану конечного автомата (неблокуючий).
     * @param current_time_ms Поточний системний час у мілісекундах.
     */
    void update(uint32_t current_time_ms);

    /**
     * @brief Отримати поточний стан конечного автомата.
     */
    ControllerState getState() const { return current_state_; }

    /**
     * @brief Перевірити, чи увімкнене навантаження (світло).
     */
    bool isLightActive() const { return light_active_; }

    /**
     * @brief Змінити тривалість затримки вимкнення освітлення.
     * @param duration_ms Нова затримка у мілісекундах.
     */
    void setHoldDuration(uint32_t duration_ms) { hold_duration_ms_ = duration_ms; }

private:
    void setRelayState(bool turn_on);

    PirSensor& sensor_;
    PowerManager& power_mgr_;
    uint8_t relay_pin_;
    uint32_t hold_duration_ms_;

    ControllerState current_state_{ControllerState::Idle};
    bool light_active_{false};
    uint32_t last_motion_timestamp_{0};
};

#endif // LIGHTING_CONTROLLER_HPP
