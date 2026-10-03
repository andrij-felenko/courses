#ifndef ESTOP_BLOCK_HPP
#define ESTOP_BLOCK_HPP

#include "SafetyTypes.hpp"
#include "EdmMonitor.hpp"

namespace safety {

// Функціональний блок безпеки двоканальної аварійної зупинки (E-Stop) з контролем EDM
class EStopBlock {
public:
    explicit EStopBlock(const EStopConfig& config = {});

    // Основна функція оновлення стану блоку безпеки в циклі PLC
    // ch1_nc_input - перший канал E-Stop (true = замкнено / норми)
    // ch2_nc_input - другий канал E-Stop (true = замкнено / норми)
    // edm_feedback_input - сигнал зворотного зв'язку NC контактів силових реле
    // reset_button_input - фізична кнопка ручного скидання аварії
    // delta_time_ms - квант часу циклу оновлення (мс)
    void update(bool ch1_nc_input,
                bool ch2_nc_input,
                bool edm_feedback_input,
                bool reset_button_input,
                uint32_t delta_time_ms);

    // Отримати стан дозволу силового виходу (true = безпечне увімкнення)
    [[nodiscard]] bool is_output_active() const noexcept;

    // Отримати поточний стан автомата безпеки
    [[nodiscard]] SafetyState get_state() const noexcept;

    // Отримати активний код помилки E-Stop
    [[nodiscard]] EStopFault get_fault() const noexcept;

    // Отримати посилання на вкладений монітор EDM
    [[nodiscard]] const EdmMonitor& get_edm_monitor() const noexcept;

    // Спроба ручного скидання станів помилок та перезапуску безпеки
    bool request_reset() noexcept;

    // Отримати поточну конфігурацію блоку
    [[nodiscard]] const EStopConfig& get_config() const noexcept;

    // Оновити конфігурацію блоку
    void set_config(const EStopConfig& config);

private:
    // Внутрішні алгоритми обробки
    void process_discrepancy(bool ch1, bool ch2, uint32_t delta_time_ms) noexcept;
    void evaluate_state_machine(bool ch1, bool ch2, bool reset_edge) noexcept;

    EStopConfig config_;
    SafetyState state_{SafetyState::WaitingForReset};
    EStopFault fault_{EStopFault::None};
    EdmMonitor edm_monitor_;

    bool output_active_{false};
    bool prev_reset_button_{false};
    uint32_t discrepancy_timer_ms_{0};
    bool discrepancy_active_{false};
};

} // namespace safety

#endif // ESTOP_BLOCK_HPP
