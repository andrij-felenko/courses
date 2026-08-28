#include <cstdint>
#include <cmath>
#include <variant>
#include <optional>
#include <string_view>

namespace drone::mission {

/* Типи подій */
struct EvTick { uint32_t timestamp_ms{0}; };
struct EvCmdStart { uint32_t timestamp_ms{0}; };
struct EvCandidateFound { uint32_t timestamp_ms{0}; float confidence{0.0F}; };
struct EvTargetConfirmed { uint32_t timestamp_ms{0}; uint32_t target_id{0}; float confidence{0.0F}; };
struct EvTargetLost { uint32_t timestamp_ms{0}; uint32_t duration_ms{0}; };
struct EvInEngageZone { uint32_t timestamp_ms{0}; float distance_m{0.0F}; };
struct EvActionComplete { uint32_t timestamp_ms{0}; };
struct EvObstacleDetected { uint32_t timestamp_ms{0}; };
struct EvObstacleCleared { uint32_t timestamp_ms{0}; };
struct EvBatteryLow { uint32_t timestamp_ms{0}; };
struct EvGeofenceBreach { uint32_t timestamp_ms{0}; };

using Event = std::variant<
    EvTick,
    EvCmdStart,
    EvCandidateFound,
    EvTargetConfirmed,
    EvTargetLost,
    EvInEngageZone,
    EvActionComplete,
    EvObstacleDetected,
    EvObstacleCleared,
    EvBatteryLow,
    EvGeofenceBreach
>;

/* Телеметрія для Guard-предикатів */
struct Telemetry {
    float energy_remaining_wh{120.0F};
    float dist_home_m{2500.0F};
    float wind_speed_ms{4.0F};
    float wind_heading_rad{0.0F};
    float uav_heading_rad{0.0F};
    float cruise_speed_ms{18.0F};
    float cruise_power_w{200.0F};
    bool gnss_3d_fix{true};
    float ekf_nis{0.4F};
    bool geofence_ok{true};
    bool payload_armed{true};
    uint8_t payload_count{2};

    [[nodiscard]] bool is_energy_sufficient_for_rtb() const noexcept {
        if (cruise_speed_ms <= 1.0F) return false;
        const float headwind = wind_speed_ms * std::cos(wind_heading_rad - uav_heading_rad);
        float ground_speed = cruise_speed_ms - headwind;
        if (ground_speed < 3.0F) ground_speed = 3.0F;

        const float time_rtb_h = (dist_home_m / ground_speed) / 3600.0F;
        const float energy_rtb_wh = cruise_power_w * time_rtb_h;
        const float energy_reserve_wh = energy_rtb_wh * 0.20F;
        return energy_remaining_wh > (energy_rtb_wh + energy_reserve_wh);
    }
};

/* Стан: Пошук */
struct StateSearch {
    static constexpr std::string_view name{"SEARCH"};
};

/* Стан: Верифікація */
struct StateAcquire {
    static constexpr std::string_view name{"ACQUIRE"};
    uint32_t entry_ms{0};
};

/* Стан: Супровід */
struct StateTrack {
    static constexpr std::string_view name{"TRACK"};
    uint32_t target_id{0};
};

/* Стан: Дія / Скид */
struct StateEngage {
    static constexpr std::string_view name{"ENGAGE"};
    uint32_t target_id{0};
};

/* Стан: Обхід перешкоди */
struct StateAvoid {
    static constexpr std::string_view name{"AVOID"};
};

/* Стан: Повернення додому */
struct StateRtb {
    static constexpr std::string_view name{"RTB"};
};

using State = std::variant<
    StateSearch,
    StateAcquire,
    StateTrack,
    StateEngage,
    StateAvoid,
    StateRtb
>;

/* Контролер місійного автомата */
class MissionHsm {
public:
    explicit MissionHsm(Telemetry telem) noexcept
        : telem_(telem), current_state_(StateSearch{}), history_state_(StateSearch{}) {}

    void dispatch(const Event& event) noexcept {
        /* 1. Рівень суперстану: Failsafe за енергією та геозоною */
        if (std::holds_alternative<EvBatteryLow>(event) || !telem_.is_energy_sufficient_for_rtb()) {
            if (!std::holds_alternative<StateRtb>(current_state_)) {
                transition_to(StateRtb{});
                return;
            }
        }

        if (std::holds_alternative<EvObstacleDetected>(event)) {
            transition_to(StateAvoid{});
            return;
        }

        /* 2. Диспетчеризація відповідно до поточного активного стану */
        std::visit([this, &event](auto& active_state) {
            handle(active_state, event);
        }, current_state_);
    }

    [[nodiscard]] const State& state() const noexcept { return current_state_; }
    void update_telemetry(const Telemetry& telem) noexcept { telem_ = telem; }

private:
    template <typename T>
    void transition_to(T new_state) noexcept {
        if (std::holds_alternative<StateSearch>(current_state_) ||
            std::holds_alternative<StateTrack>(current_state_)) {
            history_state_ = current_state_;
        }
        current_state_ = std::move(new_state);
    }

    void handle(StateSearch&, const Event& event) noexcept {
        if (const auto* cand = std::get_if<EvCandidateFound>(&event)) {
            if (cand->confidence >= 0.55F && telem_.geofence_ok) {
                transition_to(StateAcquire{ .entry_ms = cand->timestamp_ms });
            }
        }
    }

    void handle(StateAcquire& acq, const Event& event) noexcept {
        if (const auto* conf = std::get_if<EvTargetConfirmed>(&event)) {
            if (conf->confidence >= 0.80F && (telem_.ekf_nis <= 5.99F) && telem_.is_energy_sufficient_for_rtb()) {
                transition_to(StateTrack{ .target_id = conf->target_id });
            }
        } else if (const auto* tick = std::get_if<EvTick>(&event)) {
            if (tick->timestamp_ms - acq.entry_ms > 4000) {
                transition_to(StateSearch{});
            }
        }
    }

    void handle(StateTrack& track, const Event& event) noexcept {
        if (std::holds_alternative<EvInEngageZone>(event)) {
            if (telem_.payload_armed && (telem_.payload_count > 0) && telem_.is_energy_sufficient_for_rtb()) {
                transition_to(StateEngage{ .target_id = track.target_id });
            }
        } else if (const auto* lost = std::get_if<EvTargetLost>(&event)) {
            if (lost->duration_ms > 3000) {
                transition_to(StateSearch{});
            }
        }
    }

    void handle(StateEngage&, const Event& event) noexcept {
        if (std::holds_alternative<EvActionComplete>(event)) {
            transition_to(StateSearch{});
        }
    }

    void handle(StateAvoid&, const Event& event) noexcept {
        if (std::holds_alternative<EvObstacleCleared>(event)) {
            /* Відновлення стану через History */
            current_state_ = history_state_;
        }
    }

    void handle(StateRtb&, const Event&) noexcept {}

    Telemetry telem_;
    State current_state_;
    State history_state_;
};

} // namespace drone::mission
