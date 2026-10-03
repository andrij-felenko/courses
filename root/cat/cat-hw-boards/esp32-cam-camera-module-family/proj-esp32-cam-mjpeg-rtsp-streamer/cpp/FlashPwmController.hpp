#ifndef FLASH_PWM_CONTROLLER_HPP
#define FLASH_PWM_CONTROLLER_HPP

#include <driver/ledc.h>
#include <esp_err.h>
#include <cstdint>
#include <algorithm>

/**
 * @brief Клас для керування силовим світлодіодом підсвічування спалаху ESP32-CAM.
 * 
 * Використовує апаратну периферію LEDC (LED Control) для генерації ШІМ-сигналу
 * на GPIO4 із можливістю плавної зміни яскравості від 0% до 100%.
 */
class FlashPwmController {
public:
    static constexpr uint8_t DEFAULT_FLASH_PIN = 4;
    static constexpr uint32_t DEFAULT_PWM_FREQ = 5000; // 5 кГц для усунення мерехтіння
    static constexpr ledc_channel_t DEFAULT_LEDC_CHANNEL = LEDC_CHANNEL_0;
    static constexpr ledc_timer_t DEFAULT_LEDC_TIMER = LEDC_TIMER_0;
    static constexpr ledc_mode_t DEFAULT_LEDC_MODE = LEDC_LOW_SPEED_MODE;
    static constexpr ledc_timer_bit_t DEFAULT_DUTY_RES = LEDC_TIMER_8_BIT; // 0..255

    FlashPwmController() = default;

    /**
     * @brief Деструктор автоматично вимикає світлодіод і звільняє канал LEDC.
     */
    ~FlashPwmController() {
        turnOff();
    }

    // Забороняємо копіювання для запобігання конфліктам керування апаратним каналом LEDC
    FlashPwmController(const FlashPwmController&) = delete;
    FlashPwmController& operator=(const FlashPwmController&) = delete;

    // Дозволяємо переміщення
    FlashPwmController(FlashPwmController&& other) noexcept 
        : gpioPin_(other.gpioPin_), channel_(other.channel_), 
          timer_(other.timer_), currentDuty_(other.currentDuty_), isInitialized_(other.isInitialized_) {
        other.isInitialized_ = false;
    }

    FlashPwmController& operator=(FlashPwmController&& other) noexcept {
        if (this != &other) {
            turnOff();
            gpioPin_ = other.gpioPin_;
            channel_ = other.channel_;
            timer_ = other.timer_;
            currentDuty_ = other.currentDuty_;
            isInitialized_ = other.isInitialized_;
            other.isInitialized_ = false;
        }
        return *this;
    }

    /**
     * @brief Ініціалізація таймера та каналу LEDC для світлодіода спалаху.
     * @param pin Номер GPIO виводу (за замовчуванням GPIO4 для ESP32-CAM).
     * @param freq Частота ШІМ у Гц (за замовчуванням 5000 Гц).
     * @return true у разі успішного налаштування, false — у разі помилки.
     */
    bool begin(uint8_t pin = DEFAULT_FLASH_PIN, uint32_t freq = DEFAULT_PWM_FREQ) {
        gpioPin_ = pin;

        // Конфігурація апаратного таймера LEDC
        ledc_timer_config_t timerConfig = {};
        timerConfig.speed_mode       = DEFAULT_LEDC_MODE;
        timerConfig.duty_resolution  = DEFAULT_DUTY_RES;
        timerConfig.timer_num        = timer_;
        timerConfig.freq_hz          = freq;
        timerConfig.clk_cfg          = LEDC_AUTO_CLK;

        if (ledc_timer_config(&timerConfig) != ESP_OK) {
            return false;
        }

        // Конфігурація каналу LEDC
        ledc_channel_config_t channelConfig = {};
        channelConfig.gpio_num       = gpioPin_;
        channelConfig.speed_mode     = DEFAULT_LEDC_MODE;
        channelConfig.channel        = channel_;
        channelConfig.intr_type      = LEDC_INTR_DISABLE;
        channelConfig.timer_sel      = timer_;
        channelConfig.duty           = 0; // Початково вимкнено
        channelConfig.hpoint         = 0;

        if (ledc_channel_config(&channelConfig) != ESP_OK) {
            return false;
        }

        isInitialized_ = true;
        currentDuty_ = 0;
        return true;
    }

    /**
     * @brief Встановлює яскравість у значеннях скважності ШІМ (0..255).
     * @param duty Скважність ШІМ від 0 (вимкнено) до 255 (максимальна яскравість).
     */
    void setDuty(uint8_t duty) {
        if (!isInitialized_) return;

        currentDuty_ = duty;
        ledc_set_duty(DEFAULT_LEDC_MODE, channel_, currentDuty_);
        ledc_update_duty(DEFAULT_LEDC_MODE, channel_);
    }

    /**
     * @brief Встановлює яскравість підсвічування у відсотках (0..100%).
     * @param percentage Відсоток яскравості від 0% до 100%.
     */
    void setBrightnessPercent(uint8_t percentage) {
        uint8_t clamped = std::min(percentage, static_cast<uint8_t>(100));
        uint8_t duty = static_cast<uint8_t>((clamped * 255) / 100);
        setDuty(duty);
    }

    /**
     * @brief Вимикає світлодіод спалаху.
     */
    void turnOff() {
        if (isInitialized_) {
            setDuty(0);
        }
    }

    /**
     * @brief Повертає поточну скважність ШІМ (0..255).
     */
    uint8_t getDuty() const {
        return currentDuty_;
    }

    /**
     * @brief Перевіряє, чи ініціалізовано контролер.
     */
    bool isInitialized() const {
        return isInitialized_;
    }

private:
    uint8_t gpioPin_{DEFAULT_FLASH_PIN};
    ledc_channel_t channel_{DEFAULT_LEDC_CHANNEL};
    ledc_timer_t timer_{DEFAULT_LEDC_TIMER};
    uint8_t currentDuty_{0};
    bool isInitialized_{false};
};

#endif // FLASH_PWM_CONTROLLER_HPP
