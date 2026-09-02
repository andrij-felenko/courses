#pragma once

#include "escalation/protocol.hpp"
#include "escalation/trail.hpp"

#include <chrono>
#include <expected>
#include <span>
#include <string_view>
#include <variant>

namespace esc {

enum class State : std::uint8_t {
    Autonomous = 0,
    EscalationRequested,        // пакет треба зібрати й віддати в радіо
    AwaitingOperator,
    ApplyingOverride,
    FailsafeHold,
    FailsafeBacktrack,
    FailsafeSafeAbort,
    ManualRc             // перехоплення апаратним тумблером пульта
};

[[nodiscard]] std::string_view to_string(State s) noexcept;

// Команда нижньому рівню керування на цей такт
namespace cmd {
struct Continue {};
struct Hold {};
struct FollowOption { std::uint8_t option_id{}; };
struct GoTo { Pose target{}; float accept_radius_m{kAcceptRadiusM}; };
struct SafeAbort { bool persist_incident{false}; };
struct Manual {};
}  // namespace cmd

using Command = std::variant<cmd::Continue, cmd::Hold, cmd::FollowOption,
                            cmd::GoTo, cmd::SafeAbort, cmd::Manual>;

enum class Reject : std::uint8_t {
    BadFrame,
    WrongState,     // автомат уже не чекає — запізніла кнопка
    StaleId,        // відповідь на попередній інцидент
    TooLate,        // дедлайн вичерпано
    UnknownOption
};

[[nodiscard]] std::string_view to_string(Reject r) noexcept;

class Manager {
public:
    struct Inputs {
        std::chrono::milliseconds now{0ms};
        Trigger                   trigger{Trigger::None};
        float                     dist_to_obstacle_m{};
        float                     speed_mps{};
        Pose                      pose{};
        std::chrono::milliseconds last_heartbeat{0ms};
        bool                      rc_override{false};   // апаратний перемикач пульта
        bool                      maneuver_done{false}; // планувальник доробив опцію
        std::span<const Option>   options{};            // варіанти при тригері
        std::span<const std::byte> roi{};               // мініатюра спірної ділянки
    };

    struct Outputs {
        Command                    command{cmd::Continue{}};
        std::span<const std::byte> frame{};  // непорожній — віддати в радіо
    };

    explicit Manager(std::chrono::milliseconds heartbeat_timeout = 1500ms) noexcept
        : heartbeat_timeout_{heartbeat_timeout} {}

    [[nodiscard]] Outputs tick(const Inputs& in) noexcept;

    // Успіх — прийнятий option_id; відмова — причина відкидання
    [[nodiscard]] std::expected<std::uint8_t, Reject>
    handle_reply(std::span<const std::byte> frame, std::chrono::milliseconds now) noexcept;

    [[nodiscard]] State         state() const noexcept { return state_; }
    [[nodiscard]] std::uint16_t query_id() const noexcept { return query_id_; }
    [[nodiscard]] std::chrono::milliseconds deadline() const noexcept { return deadline_; }
    [[nodiscard]] std::chrono::milliseconds request_started() const noexcept { return request_started_; }
    [[nodiscard]] const Trail&  trail() const noexcept { return trail_; }

private:
    void enter(State s, std::chrono::milliseconds now) noexcept;
    void latch_trigger(const Inputs& in) noexcept;
    [[nodiscard]] std::span<const std::byte> build_frame() noexcept;

    State                     state_{State::Autonomous};
    std::chrono::milliseconds state_entered_{0ms};
    Trigger                   active_trigger_{Trigger::None};
    std::uint16_t             query_id_{0};
    std::chrono::milliseconds request_started_{0ms};
    std::chrono::milliseconds deadline_{0ms};
    std::chrono::milliseconds heartbeat_timeout_{1500ms};
    std::uint8_t              selected_option_{0};

    std::array<Option, kMaxOptions> options_{};
    std::uint8_t                    options_count_{0};
    std::array<std::byte, kRoiMax>  roi_{};
    std::uint16_t                   roi_len_{0};

    Pose  pose_at_request_{};
    float speed_at_request_{0.0f};

    Trail               trail_{};
    std::optional<Pose> backtrack_target_{};
    bool                incident_logged_{false};

    std::array<std::byte, kMtuBytes> frame_{};
};

}  // namespace esc
