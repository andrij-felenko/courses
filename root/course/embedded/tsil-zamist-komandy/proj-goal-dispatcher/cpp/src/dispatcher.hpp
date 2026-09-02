#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

#include "goal.hpp"
#include "outbox.hpp"

namespace mission {

// Увесь стан диспетчера — три паралельні масиви фіксованої довжини, індекс
// активної цілі й лічильники часу. Ніяких зв'язних списків: під час перегляду
// черги лінійка кеша тягне весь масив за одне звернення до ОЗП.
class MissionDispatcher {
public:
    explicit MissionDispatcher(Outbox& outbox) noexcept : outbox_{outbox} {}

    // Індекс слота; std::nullopt — черга насичена й витіснити нікого.
    std::optional<std::size_t> enqueue(const GoalItem& item) noexcept;

    // Один такт. Викликається з таймерного такту навігації (10–20 Гц),
    // містить лише O(N) перевірок масиву й нічого не блокує.
    [[nodiscard]] DispatcherOutput step(const VehicleTelemetry& telem, float dt_s) noexcept;

    [[nodiscard]] std::span<const GoalState> states() const noexcept {
        return {states_.data(), count_};
    }

    [[nodiscard]] GoalState state_of(std::uint32_t goal_id) const noexcept;

private:
    void emit(std::size_t idx, GoalState state) noexcept;
    void activate(std::size_t idx) noexcept;
    void compact() noexcept;
    bool evict_weakest(std::uint8_t priority) noexcept;

    [[nodiscard]] std::optional<std::size_t> select_candidate(const VehicleTelemetry& telem) noexcept;
    [[nodiscard]] static bool preconditions_met(const GoalItem& item,
                                                const VehicleTelemetry& telem) noexcept;
    [[nodiscard]] bool has_live_emergency() const noexcept;

    std::array<GoalItem, kMaxGoals> items_{};
    std::array<GoalState, kMaxGoals> states_{};
    std::array<float, kMaxGoals> elapsed_s_{};  // витіснена ціль зберігає прогрес тут
    std::size_t count_{0};
    std::optional<std::size_t> active_{};
    Outbox& outbox_;
};

}  // namespace mission
