#ifndef LASER_OUTPUT_HPP_
#define LASER_OUTPUT_HPP_

#include <cstdint>
#include <algorithm>
#include <utility>

namespace laser {

/**
 * @brief Апаратний низькорівневий інтерфейс керування таймером ШІМ та піном затвора.
 */
class IPwmHardware {
public:
    virtual ~IPwmHardware() = default;
    virtual void set_frequency_hz(uint32_t freq_hz) = 0;
    virtual void set_duty_permille(uint16_t permille) = 0; // 0..1000 (0.0% .. 100.0%)
    virtual void enable_output() = 0;
    virtual void disable_output() = 0;
    virtual void force_pin_low() = 0;
};

/**
 * @brief RAII-клас керування вихідним каскадом лазерного діода.
 * 
 * Гарантує, що при знищенні об'єкта або виникненні винятку затвор N-MOSFET транзистора
 * буде негайно притягнуто до нуля, виключаючи неконтрольовану генерацію випромінювання.
 * Забезпечує ексклюзивне володіння апаратним каналом (non-copyable, movable).
 */
class LaserOutput {
public:
    /**
     * @brief Конструктор із конфігурацією частоти ШІМ.
     * За замовчуванням вихід залишається вимкненим (safe by default).
     */
    explicit LaserOutput(IPwmHardware& hw, uint32_t pwm_frequency_hz = 25000) noexcept
        : hw_(&hw), pwm_frequency_hz_(pwm_frequency_hz) {
        hw_->force_pin_low();
        hw_->set_frequency_hz(pwm_frequency_hz_);
        hw_->set_duty_permille(0);
    }

    /**
     * @brief Деструктор RAII: примусово гасить лазер та притискає затвор до землі.
     */
    ~LaserOutput() noexcept {
        shutdown();
    }

    // Заборона копіювання: один фізичний пін - один власник
    LaserOutput(const LaserOutput&) = delete;
    LaserOutput& operator=(const LaserOutput&) = delete;

    // Дозвіл переміщення (move-семантика)
    LaserOutput(LaserOutput&& other) noexcept
        : hw_(other.hw_),
          pwm_frequency_hz_(other.pwm_frequency_hz_),
          current_duty_permille_(other.current_duty_permille_),
          is_enabled_(other.is_enabled_) {
        other.hw_ = nullptr;
        other.is_enabled_ = false;
        other.current_duty_permille_ = 0;
    }

    LaserOutput& operator=(LaserOutput&& other) noexcept {
        if (this != &other) {
            shutdown();
            hw_ = other.hw_;
            pwm_frequency_hz_ = other.pwm_frequency_hz_;
            current_duty_permille_ = other.current_duty_permille_;
            is_enabled_ = other.is_enabled_;

            other.hw_ = nullptr;
            other.is_enabled_ = false;
            other.current_duty_permille_ = 0;
        }
        return *this;
    }

    /**
     * @brief Активація генерації випромінювання із заданою шпаруватістю.
     * @param duty_permille Коефіцієнт заповнення у проміле (0..1000)
     */
    void enable(uint16_t duty_permille) noexcept {
        if (!hw_) return;
        set_duty(duty_permille);
        hw_->enable_output();
        is_enabled_ = true;
    }

    /**
     * @brief Вимкнення виходу без втрати налаштувань частоти.
     */
    void disable() noexcept {
        if (!hw_) return;
        hw_->disable_output();
        hw_->force_pin_low();
        is_enabled_ = false;
    }

    /**
     * @brief Динамічна зміна шпаруватості ШІМ (0..1000 проміле).
     */
    void set_duty(uint16_t duty_permille) noexcept {
        if (!hw_) return;
        current_duty_permille_ = std::min<uint16_t>(duty_permille, 1000);
        hw_->set_duty_permille(current_duty_permille_);
    }

    /**
     * @brief Примусове аварійне відключення.
     */
    void shutdown() noexcept {
        if (hw_) {
            hw_->disable_output();
            hw_->force_pin_low();
            is_enabled_ = false;
            current_duty_permille_ = 0;
        }
    }

    [[nodiscard]] bool is_enabled() const noexcept { return is_enabled_; }
    [[nodiscard]] uint16_t current_duty() const noexcept { return current_duty_permille_; }
    [[nodiscard]] uint32_t frequency_hz() const noexcept { return pwm_frequency_hz_; }

private:
    IPwmHardware* hw_{nullptr};
    uint32_t pwm_frequency_hz_{25000};
    uint16_t current_duty_permille_{0};
    bool is_enabled_{false};
};

} // namespace laser

#endif // LASER_OUTPUT_HPP_
