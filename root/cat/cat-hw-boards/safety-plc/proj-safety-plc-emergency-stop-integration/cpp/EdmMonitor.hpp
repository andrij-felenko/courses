#ifndef EDM_MONITOR_HPP
#define EDM_MONITOR_HPP

#include "SafetyTypes.hpp"

namespace safety {

// Клас моніторингу зворотного зв'язку зовнішніх реле/контакторів (External Device Monitoring - EDM)
class EdmMonitor {
public:
    explicit EdmMonitor(const EdmConfig& config = {})
        : config_(config) {}

    // Оновлення стану монітора в кожному циклі Safety PLC
    // safety_output_active - поточний стан безпечного виходу контролера
    // feedback_nc_input - стан розмикальних (NC) контактів зворотного зв'язку реле
    // delta_time_ms - час, що минув з попереднього циклу (мс)
    void update(bool safety_output_active, bool feedback_nc_input, uint32_t delta_time_ms) {
        // Якщо помилка вже зафіксована, вона залишається до явного скидання
        if (fault_ != EdmFaultState::None) {
            return;
        }

        // Очікуваний стан NC контактів зворотного зв'язку протилежний до стану силового виходу:
        // Вихід OFF (false) -> реле знеструмлені -> NC контакти замкнені (true)
        // Вихід ON (true) -> реле під напругою -> NC контакти розімкнені (false)
        const bool expected_nc_state = !safety_output_active;

        if (feedback_nc_input != expected_nc_state) {
            mismatch_timer_ms_ += delta_time_ms;
            if (mismatch_timer_ms_ >= config_.feedback_timeout_ms) {
                // Час перемикання перевищено, класифікуємо несправність
                if (!safety_output_active && !feedback_nc_input) {
                    // Вихід вимкнено, але NC контакт не замкнувся -> приварювання силових контактів
                    fault_ = EdmFaultState::ContactWelded;
                } else if (safety_output_active && feedback_nc_input) {
                    // Вихід увімкнено, але NC контакт не розімкнувся -> заклинювання реле
                    fault_ = EdmFaultState::ContactStuckOpen;
                } else {
                    fault_ = EdmFaultState::FeedbackTimeout;
                }
            }
        } else {
            // Стан відповідає очікуваному, скидаємо таймер неузгодженості
            mismatch_timer_ms_ = 0;
        }
    }

    // Перевірка справності ланцюга EDM
    [[nodiscard]] bool is_ok() const noexcept {
        return fault_ == EdmFaultState::None;
    }

    // Перевірка наявності апаратної помилки
    [[nodiscard]] bool is_fault() const noexcept {
        return fault_ != EdmFaultState::None;
    }

    // Отримати код апаратної помилки EDM
    [[nodiscard]] EdmFaultState get_fault() const noexcept {
        return fault_;
    }

    // Отримати поточне значення таймера неузгодженості (мс)
    [[nodiscard]] uint32_t get_mismatch_timer_ms() const noexcept {
        return mismatch_timer_ms_;
    }

    // Ручне скидання зафіксованої помилки EDM
    void reset() noexcept {
        fault_ = EdmFaultState::None;
        mismatch_timer_ms_ = 0;
    }

    // Зміна конфігураційного таймауту
    void set_config(const EdmConfig& config) noexcept {
        config_ = config;
    }

    [[nodiscard]] const EdmConfig& get_config() const noexcept {
        return config_;
    }

private:
    EdmConfig config_;
    EdmFaultState fault_{EdmFaultState::None};
    uint32_t mismatch_timer_ms_{0};
};

} // namespace safety

#endif // EDM_MONITOR_HPP
