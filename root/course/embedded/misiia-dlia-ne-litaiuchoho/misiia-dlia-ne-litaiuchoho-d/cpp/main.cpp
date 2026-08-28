#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <numbers>
#include <algorithm>

namespace navigation {

enum class MissionType : uint8_t {
    Waypoint,
    StationKeep,
    Actuate,
    WaitCondition,
    SafePark
};

enum class EngineState : uint8_t {
    Idle,
    Navigating,
    StationKeeping,
    Actuating,
    Waiting,
    Completed,
    Failsafe
};

struct GeoCoordinate {
    int32_t lat_e7{0};
    int32_t lon_e7{0};
};

struct MissionItem {
    MissionType type{MissionType::Waypoint};
    GeoCoordinate pos{};
    float target_param{0.0f};      // Радіус (м) / поріг давача / кут
    uint32_t duration_ms{0};       // Витримка / тайм-аут
    uint8_t actuator_mask{0};      // Маска реле/клапанів
};

struct VehicleState {
    GeoCoordinate pos{};
    float yaw_rad{0.0f};
    float speed_mps{0.0f};
    float battery_v{12.6f};
    float roll_deg{0.0f};
    float pitch_deg{0.0f};
    float sensor_val{0.0f};
};

struct ControlOutput {
    float steering_norm{0.0f};    // [-1.0 .. +1.0]
    float throttle_norm{0.0f};    // [-1.0 .. +1.0]
    uint8_t actuator_out{0};
};

class MissionEngine {
public:
    static constexpr size_t kMaxItems = 32;
    static constexpr float kEarthRadiusM = 6371000.0f;

    MissionEngine() = default;

    bool load_items(std::span<const MissionItem> new_items) {
        if (new_items.size() > kMaxItems) return false;
        std::copy(new_items.begin(), new_items.end(), items_.begin());
        item_count_ = static_cast<uint8_t>(new_items.size());
        current_index_ = 0;
        state_ = EngineState::Idle;
        return true;
    }

    void start(uint32_t now_ms) {
        if (item_count_ == 0) {
            state_ = EngineState::Completed;
            return;
        }
        current_index_ = 0;
        state_enter_time_ms_ = now_ms;
        state_ = EngineState::Navigating;
    }

    ControlOutput update(const VehicleState& state, uint32_t now_ms) {
        ControlOutput out{};

        // Глобальні ліміти безпеки: нахил схилу та розряд АКБ
        if (std::abs(state.roll_deg) > 30.0f || std::abs(state.pitch_deg) > 25.0f || state.battery_v < 10.5f) {
            state_ = EngineState::Failsafe;
        }

        if (state_ == EngineState::Failsafe || state_ == EngineState::Idle || state_ == EngineState::Completed) {
            return out;
        }

        if (current_index_ >= item_count_) {
            state_ = EngineState::Completed;
            return out;
        }

        const auto& cur = items_[current_index_];

        switch (cur.type) {
            case MissionType::Waypoint: {
                auto [dist_m, bearing_rad] = calculate_bearing_distance(state.pos, cur.pos);
                float heading_err = wrap_pi(bearing_rad - state.yaw_rad);

                out.steering_norm = std::clamp(heading_err * 1.2f, -1.0f, 1.0f);
                float speed_scale = std::max(0.2f, std::cos(heading_err));
                out.throttle_norm = 0.6f * speed_scale;

                if (dist_m <= cur.target_param) {
                    advance_step(now_ms);
                }
                break;
            }

            case MissionType::StationKeep: {
                auto [dist_m, bearing_rad] = calculate_bearing_distance(state.pos, cur.pos);
                float r_inner = cur.target_param;
                float r_outer = r_inner * 2.0f;

                float heading_err = wrap_pi(bearing_rad - state.yaw_rad);
                out.steering_norm = std::clamp(heading_err * 1.5f, -1.0f, 1.0f);

                if (dist_m > r_outer && !thrust_pulse_active_) {
                    thrust_pulse_active_ = true;
                    last_thrust_pulse_ms_ = now_ms;
                }

                if (thrust_pulse_active_) {
                    out.throttle_norm = 0.5f;
                    if (dist_m <= r_inner || (now_ms - last_thrust_pulse_ms_) > 4000) {
                        thrust_pulse_active_ = false;
                    }
                } else {
                    out.throttle_norm = 0.0f; // Дрейф у мертвій зоні
                }

                if (cur.duration_ms > 0 && (now_ms - state_enter_time_ms_) >= cur.duration_ms) {
                    thrust_pulse_active_ = false;
                    advance_step(now_ms);
                }
                break;
            }

            case MissionType::Actuate: {
                out.actuator_out = cur.actuator_mask;
                if ((now_ms - state_enter_time_ms_) >= cur.duration_ms) {
                    out.actuator_out = 0;
                    advance_step(now_ms);
                }
                break;
            }

            case MissionType::WaitCondition: {
                bool condition_met = (state.sensor_val >= cur.target_param);
                bool timeout = (cur.duration_ms > 0 && (now_ms - state_enter_time_ms_) >= cur.duration_ms);

                if (condition_met || timeout) {
                    advance_step(now_ms);
                }
                break;
            }

            case MissionType::SafePark: {
                state_ = EngineState::Completed;
                break;
            }
        }

        return out;
    }

    [[nodiscard]] EngineState state() const noexcept { return state_; }
    [[nodiscard]] uint8_t current_index() const noexcept { return current_index_; }

private:
    std::array<MissionItem, kMaxItems> items_{};
    uint8_t item_count_{0};
    uint8_t current_index_{0};
    EngineState state_{EngineState::Idle};
    uint32_t state_enter_time_ms_{0};
    uint32_t last_thrust_pulse_ms_{0};
    bool thrust_pulse_active_{false};

    void advance_step(uint32_t now_ms) noexcept {
        current_index_++;
        state_enter_time_ms_ = now_ms;
    }

    static float wrap_pi(float angle_rad) noexcept {
        constexpr float pi = std::numbers::pi_v<float>;
        while (angle_rad > pi) angle_rad -= 2.0f * pi;
        while (angle_rad < -pi) angle_rad += 2.0f * pi;
        return angle_rad;
    }

    static std::pair<float, float> calculate_bearing_distance(
        const GeoCoordinate& from, const GeoCoordinate& to) noexcept {
        constexpr float deg_to_rad = std::numbers::pi_v<float> / 180.0f;
        float d_lat = static_cast<float>(to.lat_e7 - from.lat_e7) * 1e-7f * deg_to_rad;
        float d_lon = static_cast<float>(to.lon_e7 - from.lon_e7) * 1e-7f * deg_to_rad;
        float lat_mean = static_cast<float>(from.lat_e7 + to.lat_e7) * 0.5f * 1e-7f * deg_to_rad;

        float north = d_lat * kEarthRadiusM;
        float east = d_lon * kEarthRadiusM * std::cos(lat_mean);

        float dist = std::sqrt(north * north + east * east);
        float bearing = std::atan2(east, north);
        return {dist, bearing};
    }
};

} // namespace navigation
