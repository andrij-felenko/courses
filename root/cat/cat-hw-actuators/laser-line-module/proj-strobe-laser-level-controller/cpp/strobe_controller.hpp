#ifndef STROBE_CONTROLLER_HPP_
#define STROBE_CONTROLLER_HPP_

#include "laser_output.hpp"
#include <cstdint>
#include <algorithm>

namespace laser {

/**
 * @brief Режим роботи контролера стробування.
 */
enum class StrobeMode : uint8_t {
    Continuous = 0,     // Постійне світіння з ШІМ-регулюванням
    ExternalTrigger = 1,// Синхронізація від зовнішнього імпульсу камери
    SoftwareStrobe = 2  // Одиночний програмний спалах
};

/**
 * @brief Конфігурація параметрів стробування лазера.
 */
struct StrobeTimingConfig {
    uint32_t pulse_width_us{250};        // Тривалість спалаху (експозиція, мкс)
    uint32_t trigger_delay_us{10};       // Затримка між фронтом тригера та вмиканням лазера (мкс)
    uint32_t max_pulse_width_us{2000};   // Апаратний ліміт тривалості імпульсу
    StrobeMode mode{StrobeMode::ExternalTrigger};
};

/**
 * @brief Контролер синхронізації та генерації прецизійних мікросекундних спалахів.
 * 
 * Працює в тандемі з LaserOutput: за зовнішнім апаратним тригером від камери
 * формує строб заданої тривалості, синхронізуючи випромінювання з вікном експозиції.
 */
class StrobeController {
public:
    explicit StrobeController(LaserOutput& output, const StrobeTimingConfig& config = {}) noexcept
        : output_(output), config_(config) {}

    /**
     * @brief Оновлення конфігурації часу стробування з валідацією.
     */
    bool configure(const StrobeTimingConfig& config) noexcept {
        if (config.pulse_width_us == 0 || config.pulse_width_us > config.max_pulse_width_us) {
            return false;
        }
        config_ = config;
        return true;
    }

    /**
     * @brief Обробник зовнішнього апаратного переривання (фронт тригера від камери).
     * @param target_duty_permille Поточна дозволена шпаруватість (з урахуванням адаптації та захисту)
     */
    void on_external_trigger(uint16_t target_duty_permille) noexcept {
        if (config_.mode != StrobeMode::ExternalTrigger && config_.mode != StrobeMode::SoftwareStrobe) {
            return;
        }

        // Активація спалаху через LaserOutput
        output_.enable(target_duty_permille);
        strobe_count_++;
        last_pulse_width_us_ = config_.pulse_width_us;
        is_strobe_active_ = true;
    }

    /**
     * @brief Завершення активного імпульсу стробу (викликається таймером після закінчення pulse_width_us).
     */
    void on_pulse_complete() noexcept {
        if (is_strobe_active_) {
            output_.disable();
            is_strobe_active_ = false;
        }
    }

    /**
     * @brief Ручний запуск одиночного стробу.
     */
    void trigger_single_shot(uint16_t target_duty_permille) noexcept {
        config_.mode = StrobeMode::SoftwareStrobe;
        on_external_trigger(target_duty_permille);
    }

    [[nodiscard]] uint32_t strobe_count() const noexcept { return strobe_count_; }
    [[nodiscard]] bool is_active() const noexcept { return is_strobe_active_; }
    [[nodiscard]] const StrobeTimingConfig& config() const noexcept { return config_; }

private:
    LaserOutput& output_;
    StrobeTimingConfig config_{};
    uint32_t strobe_count_{0};
    uint32_t last_pulse_width_us_{0};
    bool is_strobe_active_{false};
};

} // namespace laser

#endif // STROBE_CONTROLLER_HPP_
