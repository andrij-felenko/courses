#pragma once

#include "alarm_types.hpp"
#include <array>
#include <vector>
#include <string_view>
#include <span>

namespace isa18_2 {

/**
 * @brief Диспетчер та раціоналізатор тривог за стандартом ISA-18.2.
 */
class AlarmRationalizer {
public:
    AlarmRationalizer() noexcept;

    /**
     * @brief Реєстрація конфігурації тривоги.
     */
    bool register_alarm(const AlarmConfig& cfg) noexcept;

    /**
     * @brief Встановлення поточного експлуатаційного стану системи.
     */
    void set_system_state(SystemStateMask state, std::chrono::milliseconds now) noexcept;

    /**
     * @brief Оновлення виміряного значення сигналу.
     */
    void update_value(uint16_t alarm_id, float value, std::chrono::milliseconds now) noexcept;

    /**
     * @brief Періодичний такт обробки логіки автомата станів та пригнічення.
     */
    void process(std::chrono::milliseconds now) noexcept;

    /**
     * @brief Квитування тривоги оператором.
     */
    bool acknowledge(uint16_t alarm_id, std::chrono::milliseconds now) noexcept;

    /**
     * @brief Відкладення тривоги (Shelve) на задану тривалість.
     */
    bool shelve(uint16_t alarm_id, std::chrono::milliseconds duration, std::chrono::milliseconds now) noexcept;

    /**
     * @brief Ручне повернення тривоги з відкладеного стану.
     */
    bool unshelve(uint16_t alarm_id, std::chrono::milliseconds now) noexcept;

    /**
     * @brief Отримання списку активних тривог, відсортованих за пріоритетом для виведення на HMI.
     */
    [[nodiscard]] std::vector<uint16_t> get_active_hmi_alarms() const;

    [[nodiscard]] const AlarmConfig& get_config(uint16_t alarm_id) const;
    [[nodiscard]] const AlarmRuntime& get_runtime(uint16_t alarm_id) const;
    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] bool is_alarm_flood() const noexcept { return is_alarm_flood_; }
    [[nodiscard]] size_t alarms_in_rate_window() const noexcept { return alarms_in_window_; }

private:
    void evaluate_raw_trip(const AlarmConfig& cfg, AlarmRuntime& rt) noexcept;
    void update_chatter(const AlarmConfig& cfg, AlarmRuntime& rt, std::chrono::milliseconds now) noexcept;
    void add_rate_event(std::chrono::milliseconds now) noexcept;
    void update_rate_metrics(std::chrono::milliseconds now) noexcept;

    std::array<AlarmConfig, MaxAlarms> configs_{};
    std::array<AlarmRuntime, MaxAlarms> runtimes_{};
    size_t count_{0};
    SystemStateMask current_sys_state_{SystemStateMask::ColdBoot};

    std::array<std::chrono::milliseconds, MaxAlarms * 2> rate_history_{};
    size_t rate_head_{0};
    size_t rate_tail_{0};
    size_t alarms_in_window_{0};
    bool is_alarm_flood_{false};

    uint32_t total_trips_{0};
    uint32_t total_acks_{0};
    uint32_t total_suppressions_{0};
    uint32_t total_chatter_events_{0};
};

} // namespace isa18_2
