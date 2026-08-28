#include <cstdint>
#include <cmath>
#include <array>
#include <variant>
#include <optional>
#include <string_view>
#include <iostream>
#include <cassert>

namespace drone::mission {

inline constexpr size_t kQueueCapacity = 32;
inline constexpr uint32_t kTargetTrackTimeoutMs = 3000;
inline constexpr uint32_t kAcquireTimeoutMs      = 4000;
inline constexpr uint32_t kVerifyTimeoutMs       = 2000;

/* ── 1. Структура опису цілі ── */
struct Target {
    uint32_t id{0};
    float latitude{0.0F};
    float longitude{0.0F};
    float altitude{0.0F};
    float confidence{0.0F};
    float distance_m{0.0F};
    float nis{0.0F};
};

/* ── 2. Строго типізований набір подій ── */
struct EvTick { uint32_t timestamp_ms{0}; };
struct EvCmdStart { uint32_t timestamp_ms{0}; };
struct EvCandidateDetected { uint32_t timestamp_ms{0}; Target target{}; };
struct EvTargetLocked { uint32_t timestamp_ms{0}; Target target{}; };
struct EvTargetLost { uint32_t timestamp_ms{0}; };
struct EvWithinEngageRange { uint32_t timestamp_ms{0}; };
struct EvPayloadReleased { uint32_t timestamp_ms{0}; };
struct EvVerifyComplete { uint32_t timestamp_ms{0}; };
struct EvObstacleDetected { uint32_t timestamp_ms{0}; };
struct EvObstacleCleared { uint32_t timestamp_ms{0}; };
struct EvBatteryCritical { uint32_t timestamp_ms{0}; };
struct EvGeofenceBreach { uint32_t timestamp_ms{0}; };
struct EvCmdAbort { uint32_t timestamp_ms{0}; };

using MissionEvent = std::variant<
    EvTick,
    EvCmdStart,
    EvCandidateDetected,
    EvTargetLocked,
    EvTargetLost,
    EvWithinEngageRange,
    EvPayloadReleased,
    EvVerifyComplete,
    EvObstacleDetected,
    EvObstacleCleared,
    EvBatteryCritical,
    EvGeofenceBreach,
    EvCmdAbort
>;

/* ── 3. Телеметрія та стан борта ── */
struct Telemetry {
    float battery_voltage{24.5F};
    float battery_soc{0.95F};
    float energy_remaining_wh{140.0F};
    float dist_to_home_m{2000.0F};
    float wind_speed_ms{3.0F};
    float wind_heading_rad{0.0F};
    float uav_heading_rad{0.0F};
    float cruise_speed_ms{20.0F};
    float cruise_power_w{220.0F};
    bool gnss_3d_fix{true};
    float gnss_hdop{0.8F};
    float ekf_nis{0.2F};
    bool geofence_ok{true};
    bool payload_armed{true};
    uint8_t payload_remaining{2};
    float obstacle_distance_m{50.0F};

    [[nodiscard]] bool is_energy_sufficient_for_rtb() const noexcept {
        if (cruise_speed_ms <= 1.0F) return false;
        const float headwind = wind_speed_ms * std::cos(wind_heading_rad - uav_heading_rad);
        float ground_speed = cruise_speed_ms - headwind;
        if (ground_speed < 3.0F) ground_speed = 3.0F;

        const float time_rtb_h = (dist_to_home_m / ground_speed) / 3600.0F;
        const float energy_rtb_wh = cruise_power_w * time_rtb_h;
        const float energy_reserve_wh = energy_rtb_wh * 0.20F;

        return energy_remaining_wh > (energy_rtb_wh + energy_reserve_wh);
    }

    [[nodiscard]] bool are_sensors_healthy() const noexcept {
        return gnss_3d_fix && (gnss_hdop <= 1.3F) && (ekf_nis <= 1.0F);
    }

    [[nodiscard]] static constexpr bool is_target_nis_valid(float nis) noexcept {
        return nis <= 5.99F;
    }
};

/* ── 4. Дескриптори станів ── */
struct StateIdle { static constexpr std::string_view name{"IDLE"}; };
struct StateSearch { static constexpr std::string_view name{"SEARCH"}; };
struct StateAcquire { static constexpr std::string_view name{"ACQUIRE"}; uint32_t entry_ms{0}; Target target{}; };
struct StateTrack { static constexpr std::string_view name{"TRACK"}; uint32_t last_seen_ms{0}; Target target{}; };
struct StateEngage { static constexpr std::string_view name{"ENGAGE"}; Target target{}; };
struct StateVerify { static constexpr std::string_view name{"VERIFY"}; uint32_t entry_ms{0}; };
struct StateAvoid { static constexpr std::string_view name{"AVOID"}; };
struct StateRtb { static constexpr std::string_view name{"RTB"}; };
struct StateAbort { static constexpr std::string_view name{"ABORT"}; };

using State = std::variant<
    StateIdle,
    StateSearch,
    StateAcquire,
    StateTrack,
    StateEngage,
    StateVerify,
    StateAvoid,
    StateRtb,
    StateAbort
>;

/* ── 5. Безблокувальна черга подій C++ ── */
template <typename T, size_t Capacity>
class SpscQueue {
public:
    constexpr SpscQueue() noexcept = default;

    bool push(const T& item) noexcept {
        const size_t next_head = (head_ + 1) % Capacity;
        if (next_head == tail_) return false;
        buffer_[head_] = item;
        head_ = next_head;
        return true;
    }

    bool pop(T& item) noexcept {
        if (tail_ == head_) return false;
        item = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        return true;
    }

private:
    std::array<T, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
};

/* ── 6. Ієрархічний контролер місійного автомата ── */
class MissionHsmEngine {
public:
    explicit MissionHsmEngine(Telemetry telem) noexcept
        : telem_(telem), current_state_(StateIdle{}), history_state_(StateSearch{}) {}

    bool post_event(const MissionEvent& event) noexcept {
        return queue_.push(event);
    }

    void process_queue() noexcept {
        MissionEvent event;
        while (queue_.pop(event)) {
            current_time_ms_ = get_timestamp(event);

            /* 1. Обробка глобальних умов суперстану OPERATIONAL */
            if (std::holds_alternative<EvBatteryCritical>(event) || !telem_.is_energy_sufficient_for_rtb()) {
                if (!std::holds_alternative<StateRtb>(current_state_) &&
                    !std::holds_alternative<StateAbort>(current_state_)) {
                    transition_to(StateRtb{});
                    continue;
                }
            }

            if (std::holds_alternative<EvGeofenceBreach>(event)) {
                transition_to(StateAbort{});
                continue;
            }

            if (std::holds_alternative<EvCmdAbort>(event)) {
                transition_to(StateRtb{});
                continue;
            }

            if (std::holds_alternative<EvObstacleDetected>(event)) {
                transition_to(StateAvoid{});
                continue;
            }

            /* 2. Поліморфна диспетчеризація поточного стану */
            std::visit([this, &event](auto& active_state) {
                handle(active_state, event);
            }, current_state_);
        }
    }

    [[nodiscard]] const State& state() const noexcept { return current_state_; }
    [[nodiscard]] Telemetry& telemetry() noexcept { return telem_; }
    [[nodiscard]] const Telemetry& telemetry() const noexcept { return telem_; }
    [[nodiscard]] bool was_payload_released() const noexcept { return payload_released_; }

private:
    template <typename T>
    void transition_to(T new_state) noexcept {
        /* Збереження стану в історію */
        if (std::holds_alternative<StateSearch>(current_state_) ||
            std::holds_alternative<StateTrack>(current_state_)) {
            history_state_ = current_state_;
        }
        current_state_ = std::move(new_state);
        transition_count_++;
    }

    static uint32_t get_timestamp(const MissionEvent& event) noexcept {
        return std::visit([](const auto& e) noexcept { return e.timestamp_ms; }, event);
    }

    void handle(StateIdle&, const MissionEvent& event) noexcept {
        if (std::holds_alternative<EvCmdStart>(event)) {
            if (telem_.are_sensors_healthy() && telem_.geofence_ok && telem_.is_energy_sufficient_for_rtb()) {
                transition_to(StateSearch{});
            }
        }
    }

    void handle(StateSearch&, const MissionEvent& event) noexcept {
        if (const auto* cand = std::get_if<EvCandidateDetected>(&event)) {
            if (cand->target.confidence >= 0.55F && telem_.geofence_ok) {
                transition_to(StateAcquire{ .entry_ms = current_time_ms_, .target = cand->target });
            }
        }
    }

    void handle(StateAcquire& acq, const MissionEvent& event) noexcept {
        if (const auto* lock = std::get_if<EvTargetLocked>(&event)) {
            if (lock->target.confidence >= 0.80F && 
                Telemetry::is_target_nis_valid(lock->target.nis) &&
                telem_.are_sensors_healthy() &&
                telem_.is_energy_sufficient_for_rtb()) {
                transition_to(StateTrack{ .last_seen_ms = current_time_ms_, .target = lock->target });
            }
        } else if (std::holds_alternative<EvTick>(event)) {
            if (current_time_ms_ - acq.entry_ms > kAcquireTimeoutMs) {
                transition_to(StateSearch{});
            }
        }
    }

    void handle(StateTrack& track, const MissionEvent& event) noexcept {
        if (std::holds_alternative<EvWithinEngageRange>(event)) {
            if (telem_.payload_armed && telem_.payload_remaining > 0 &&
                telem_.geofence_ok && telem_.is_energy_sufficient_for_rtb()) {
                payload_released_ = true;
                if (telem_.payload_remaining > 0) telem_.payload_remaining--;
                transition_to(StateEngage{ .target = track.target });
            }
        } else if (std::holds_alternative<EvTargetLost>(event) || std::holds_alternative<EvTick>(event)) {
            if (current_time_ms_ - track.last_seen_ms > kTargetTrackTimeoutMs) {
                transition_to(StateSearch{});
            }
        }
    }

    void handle(StateEngage&, const MissionEvent& event) noexcept {
        if (std::holds_alternative<EvPayloadReleased>(event)) {
            transition_to(StateVerify{ .entry_ms = current_time_ms_ });
        }
    }

    void handle(StateVerify& ver, const MissionEvent& event) noexcept {
        if (std::holds_alternative<EvVerifyComplete>(event) || std::holds_alternative<EvTick>(event)) {
            if (current_time_ms_ - ver.entry_ms >= kVerifyTimeoutMs) {
                if (telem_.payload_remaining > 0 && telem_.is_energy_sufficient_for_rtb()) {
                    transition_to(StateSearch{});
                } else {
                    transition_to(StateRtb{});
                }
            }
        }
    }

    void handle(StateAvoid&, const MissionEvent& event) noexcept {
        if (std::holds_alternative<EvObstacleCleared>(event)) {
            /* Відновлення стану з історії */
            current_state_ = history_state_;
        }
    }

    void handle(StateRtb&, const MissionEvent&) noexcept {}
    void handle(StateAbort&, const MissionEvent&) noexcept {}

    Telemetry telem_;
    State current_state_;
    State history_state_;
    SpscQueue<MissionEvent, kQueueCapacity> queue_{};
    uint32_t current_time_ms_{0};
    uint32_t transition_count_{0};
    bool payload_released_{false};
};

} // namespace drone::mission

/* ── 7. Блок юніт-тестування C++ ── */
int main() {
    using namespace drone::mission;

    Telemetry telem{};
    MissionHsmEngine fsm{telem};

    assert(std::holds_alternative<StateIdle>(fsm.state()));

    /* Тест 1: Старт місії -> SEARCH */
    fsm.post_event(EvCmdStart{ .timestamp_ms = 100 });
    fsm.process_queue();
    assert(std::holds_alternative<StateSearch>(fsm.state()));

    /* Тест 2: Виявлення кандидата -> ACQUIRE */
    fsm.post_event(EvCandidateDetected{
        .timestamp_ms = 500,
        .target = Target{ .id = 42, .confidence = 0.68F, .nis = 0.4F }
    });
    fsm.process_queue();
    assert(std::holds_alternative<StateAcquire>(fsm.state()));

    /* Тест 3: Захоплення цілі -> TRACK */
    fsm.post_event(EvTargetLocked{
        .timestamp_ms = 900,
        .target = Target{ .id = 42, .confidence = 0.91F, .nis = 1.1F }
    });
    fsm.process_queue();
    assert(std::holds_alternative<StateTrack>(fsm.state()));

    /* Тест 4: Перешкода під час наведення -> AVOID -> відновлення в TRACK */
    fsm.post_event(EvObstacleDetected{ .timestamp_ms = 1200 });
    fsm.process_queue();
    assert(std::holds_alternative<StateAvoid>(fsm.state()));

    fsm.post_event(EvObstacleCleared{ .timestamp_ms = 1800 });
    fsm.process_queue();
    assert(std::holds_alternative<StateTrack>(fsm.state()));

    /* Тест 5: Зближення на дистанцію скиду -> ENGAGE -> VERIFY */
    fsm.post_event(EvWithinEngageRange{ .timestamp_ms = 2200 });
    fsm.process_queue();
    assert(std::holds_alternative<StateEngage>(fsm.state()));
    assert(fsm.was_payload_released() == true);

    fsm.post_event(EvPayloadReleased{ .timestamp_ms = 2300 });
    fsm.process_queue();
    assert(std::holds_alternative<StateVerify>(fsm.state()));

    /* Тест 6: Завершення верифікації (залишився 1 заряд) -> SEARCH */
    fsm.post_event(EvVerifyComplete{ .timestamp_ms = 4500 });
    fsm.process_queue();
    assert(std::holds_alternative<StateSearch>(fsm.state()));

    /* Тест 7: Порушення меж геозони -> ABORT */
    fsm.post_event(EvGeofenceBreach{ .timestamp_ms = 6000 });
    fsm.process_queue();
    assert(std::holds_alternative<StateAbort>(fsm.state()));

    std::cout << "ALL MISSION HSM C++ UNIT TESTS PASSED SUCCESSFULLY!" << std::endl;
    return 0;
}
