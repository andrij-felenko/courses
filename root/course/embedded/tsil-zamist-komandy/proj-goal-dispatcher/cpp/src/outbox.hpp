#pragma once

#include <array>
#include <atomic>
#include <cstdint>
#include <optional>

#include "goal.hpp"

namespace mission {

// Номери повідомлень MAVLink Mission Protocol — сталі самого протоколу.
enum class MavlinkMsg : std::uint16_t {
    MissionCurrent = 42,
    MissionItemReached = 46,
    MissionAck = 47
};

// MAV_MISSION_RESULT — код у полі type пакета MISSION_ACK.
enum class MavMissionResult : std::uint8_t {
    Accepted = 0,
    Error = 1,
    NoSpace = 4,
    Denied = 13,
    Cancelled = 14
};

// Готовий до пакування зріз переходу скінченного автомата. Саме пакування
// робить згенерована бібліотека MAVLink уже в потоці зв'язку.
struct MissionEvent {
    std::uint32_t id{0};
    GoalState state{GoalState::Empty};
    MavlinkMsg msg{MavlinkMsg::MissionAck};
    MavMissionResult result{MavMissionResult::Error};
    Vec3 target{};
};

[[nodiscard]] MissionEvent make_event(const GoalItem& goal, GoalState state) noexcept;
[[nodiscard]] MissionEvent make_no_space_event(const GoalItem& goal) noexcept;

// Односторонній міст диспетчер → потік телеметрії: один виробник, один
// споживач, жодного м'ютекса. Крок диспетчера не має права заблокуватися
// на зайнятому радіоканалі, тож переповнення тут — втрата події, не чекання.
class Outbox {
public:
    bool push(const MissionEvent& ev) noexcept;              // бік диспетчера
    [[nodiscard]] std::optional<MissionEvent> pop() noexcept; // бік телеметрії

    [[nodiscard]] std::uint32_t dropped() const noexcept {
        return dropped_.load(std::memory_order_relaxed);
    }

private:
    // Степінь двійки — щоб індекс брався маскою, а не діленням.
    static constexpr std::uint32_t kCapacity = 16;

    std::array<MissionEvent, kCapacity> slots_{};
    std::atomic<std::uint32_t> head_{0};     // рухає лише виробник
    std::atomic<std::uint32_t> tail_{0};     // рухає лише споживач
    std::atomic<std::uint32_t> dropped_{0};
};

}  // namespace mission
