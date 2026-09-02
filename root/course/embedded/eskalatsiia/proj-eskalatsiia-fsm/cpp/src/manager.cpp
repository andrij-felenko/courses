#include "escalation/manager.hpp"

#include "escalation/deadline.hpp"

#include <algorithm>
#include <cmath>

namespace esc {
namespace {

// Параметри платформи: логістичний ровер 350 кг
constexpr float kBrakingDecel = 2.0f;
constexpr float kSafetyMargin = 4.0f;
constexpr auto  kSensorLag    = 200ms;
// Скільки стоїмо на місці, перш ніж почати відкат
constexpr auto  kHoldBeforeBacktrack = 5000ms;

}  // namespace

void Manager::enter(State s, std::chrono::milliseconds now) noexcept {
    state_         = s;
    state_entered_ = now;
}

// Фіксуємо кінематику й варіанти на момент тригера: апарат далі рухається,
// а оператор бачить саме ту сцену, яку йому надіслали.
void Manager::latch_trigger(const Inputs& in) noexcept {
    active_trigger_   = in.trigger;
    ++query_id_;                       // монотонно, без повторів
    request_started_  = in.now;
    pose_at_request_  = in.pose;
    speed_at_request_ = in.speed_mps;
    selected_option_  = 0;

    options_count_ = static_cast<std::uint8_t>(std::min(in.options.size(), kMaxOptions));
    std::copy_n(in.options.begin(), options_count_, options_.begin());

    roi_len_ = 0;
    if (!in.roi.empty() && in.roi.size() <= kRoiMax) {
        std::copy(in.roi.begin(), in.roi.end(), roi_.begin());
        roi_len_ = static_cast<std::uint16_t>(in.roi.size());
    }
}

std::span<const std::byte> Manager::build_frame() noexcept {
    Query q;
    q.query_id  = query_id_;
    q.timestamp = request_started_;
    q.deadline  = deadline_;
    q.trigger   = active_trigger_;
    q.position  = {pose_at_request_.x, pose_at_request_.y, pose_at_request_.z};
    q.velocity  = {speed_at_request_ * std::cos(pose_at_request_.yaw),
                   speed_at_request_ * std::sin(pose_at_request_.yaw),
                   0.0f};
    q.options = std::span<const Option>{options_.data(), options_count_};
    q.roi     = std::span<const std::byte>{roi_.data(), roi_len_};

    const auto packed = pack_query(q, frame_);
    return packed ? *packed : std::span<const std::byte>{};
}

Manager::Outputs Manager::tick(const Inputs& in) noexcept {
    Outputs out{};

    // Пріоритет нуль: апаратний тумблер пульта б'є все й скидає автомат
    if (in.rc_override) {
        if (state_ != State::ManualRc) {
            active_trigger_   = Trigger::None;
            selected_option_  = 0;
            backtrack_target_.reset();
            enter(State::ManualRc, in.now);
        }
        out.command = cmd::Manual{};
        return out;
    }
    if (state_ == State::ManualRc) {
        enter(State::Autonomous, in.now);   // тумблер відпущено
    }

    // chrono рахує різницю зі знаком — переповнення лічильника нас не турбує
    const bool link_alive = (in.now - in.last_heartbeat) <= heartbeat_timeout_;

    // Слід пишемо лише коли справді їдемо вперед
    if (state_ == State::Autonomous || state_ == State::ApplyingOverride) {
        trail_.push_if_moved(in.pose);
    }

    switch (state_) {
        case State::Autonomous:
            if (in.trigger != Trigger::None && !in.options.empty()) {
                latch_trigger(in);
                deadline_ = deadline_for(in.dist_to_obstacle_m, in.speed_mps,
                                         kBrakingDecel, kSafetyMargin, kSensorLag);
                if (deadline_ == 0ms) {
                    // Часу на діалог немає — гальмуємо, оператор дізнається постфактум
                    enter(State::FailsafeHold, in.now);
                    out.command = cmd::Hold{};
                } else {
                    enter(State::EscalationRequested, in.now);
                }
            }
            break;

        case State::EscalationRequested: {
            const auto frame = build_frame();
            if (frame.empty()) {
                // Спитати не вийшло — поводимося як при мовчанні
                enter(State::FailsafeHold, in.now);
                out.command = cmd::Hold{};
            } else {
                out.frame = frame;
                enter(State::AwaitingOperator, in.now);
            }
            break;
        }

        case State::AwaitingOperator:
            if (!link_alive || (in.now - request_started_) >= deadline_) {
                enter(State::FailsafeHold, in.now);
                out.command = cmd::Hold{};
            }
            // До дедлайну рух триває: його й рахували так, щоб гальма ще встигли
            break;

        case State::ApplyingOverride:
            out.command = cmd::FollowOption{selected_option_};
            if (in.maneuver_done) {
                active_trigger_ = Trigger::None;
                enter(State::Autonomous, in.now);
            }
            break;

        case State::FailsafeHold:
            out.command = cmd::Hold{};
            if ((in.now - state_entered_) > kHoldBeforeBacktrack) {
                backtrack_target_.reset();
                enter(State::FailsafeBacktrack, in.now);
            }
            break;

        case State::FailsafeBacktrack:
            // Знімаємо точки, доки не знайдемо ту, до якої ще треба доїхати
            while (!backtrack_target_ ||
                   dist2d(in.pose, *backtrack_target_) <= kBacktrackRadiusM) {
                backtrack_target_ = trail_.pop_reverse();
                if (!backtrack_target_) {
                    break;   // історія вичерпана
                }
            }
            if (backtrack_target_) {
                out.command = cmd::GoTo{*backtrack_target_, kBacktrackRadiusM};
            } else {
                enter(State::FailsafeSafeAbort, in.now);
                const bool first = !incident_logged_;
                incident_logged_ = true;
                out.command = cmd::SafeAbort{first};
            }
            break;

        case State::FailsafeSafeAbort: {
            const bool first = !incident_logged_;
            incident_logged_ = true;
            out.command = cmd::SafeAbort{first};
            break;
        }

        case State::ManualRc:
            out.command = cmd::Manual{};
            break;
    }

    return out;
}

std::expected<std::uint8_t, Reject>
Manager::handle_reply(std::span<const std::byte> frame, std::chrono::milliseconds now) noexcept {
    const auto rep = unpack_reply(frame);
    if (!rep) {
        return std::unexpected{Reject::BadFrame};
    }
    // Три бар'єри поспіль; спрацював будь-який — приводів не чіпаємо взагалі
    if (state_ != State::AwaitingOperator) {
        return std::unexpected{Reject::WrongState};
    }
    if (rep->query_id != query_id_) {
        return std::unexpected{Reject::StaleId};
    }
    if ((now - request_started_) > deadline_) {
        return std::unexpected{Reject::TooLate};
    }

    const std::span<const Option> offered{options_.data(), options_count_};
    const bool known = std::ranges::any_of(
        offered, [&](const Option& o) { return o.id == rep->option_id; });
    if (!known) {
        return std::unexpected{Reject::UnknownOption};
    }

    selected_option_ = rep->option_id;
    enter(State::ApplyingOverride, now);
    return selected_option_;
}

std::string_view to_string(State s) noexcept {
    switch (s) {
        case State::Autonomous:        return "Autonomous";
        case State::EscalationRequested:      return "EscalationRequested";
        case State::AwaitingOperator:  return "AwaitingOperator";
        case State::ApplyingOverride:  return "ApplyingOverride";
        case State::FailsafeHold:      return "FailsafeHold";
        case State::FailsafeBacktrack: return "FailsafeBacktrack";
        case State::FailsafeSafeAbort: return "FailsafeSafeAbort";
        case State::ManualRc:          return "ManualRc";
    }
    return "?";
}

std::string_view to_string(Reject r) noexcept {
    switch (r) {
        case Reject::BadFrame:      return "битий кадр";
        case Reject::WrongState:    return "автомат уже не чекає";
        case Reject::StaleId:       return "чужий query_id";
        case Reject::TooLate:       return "після дедлайну";
        case Reject::UnknownOption: return "невідома опція";
    }
    return "?";
}

}  // namespace esc
