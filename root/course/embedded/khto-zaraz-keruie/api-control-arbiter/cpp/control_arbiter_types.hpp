#pragma once

#include "control_arbiter_types.hpp"
#include <span>

namespace embedded::control {

/**
 * @brief Клас пріоритетного селектора та безударного фільтра каналів керування.
 */
class ControlArbiter {
public:
    ControlArbiter() noexcept;

    /**
     * @brief Налаштувати часові пороги та ліміти наростання для джерела.
     */
    bool configure_source(SourceId id, const SourceConfig& cfg) noexcept;

    /**
     * @brief Зафіксувати надходження сигналу життєздатності (watchdog feed).
     */
    void feed_heartbeat(SourceId id, Microseconds now) noexcept;

    /**
     * @brief Передати нову уставку від каналу зв'язку.
     */
    void submit_setpoint(SourceId id, const Setpoint& sp, Microseconds now) noexcept;

    /**
     * @brief Виконати арбітраж та обчислити згладжену вихідну уставку.
     * @param now Поточний монотонний час.
     * @return Результуюча уставка, готова для подачі у внутрішній каскад ПІД.
     */
    Setpoint evaluate(Microseconds now) noexcept;

    /**
     * @brief Отримати поточне активне джерело авторитету.
     */
    [[nodiscard]] SourceId active_source() const noexcept { return active_source_; }

    /**
     * @brief Захоплення поточного стану апарата для безударного рестарту.
     */
    void capture_state(std::span<const float, 4> current_state, Microseconds now) noexcept;

    /**
     * @brief Отримати діагностичний стан слота.
     */
    [[nodiscard]] SourceState source_state(SourceId id) const noexcept;

    /**
     * @brief Кількість перемикань авторитету з моменту запуску.
     */
    [[nodiscard]] uint32_t transition_count() const noexcept { return transitions_; }

private:
    struct Slot {
        Setpoint raw_sp{};
        Microseconds last_heartbeat{0};
        Microseconds last_packet{0};
        SourceConfig config{};
        SourceState state{SourceState::Inactive};
        bool configured{false};
    };

    std::array<Slot, SourceCount> slots_{};
    SourceId active_source_{SourceId::None};
    SourceId previous_source_{SourceId::None};
    Setpoint smoothed_output_{};
    Microseconds last_eval_time_{0};
    uint32_t transitions_{0};

    [[nodiscard]] bool check_stick_activity(const Slot& slot) const noexcept;
    void apply_slew_rate(const Setpoint& target, float dt_sec) noexcept;
};

} // namespace embedded::control
