#include <chrono>
#include <cmath>
#include <algorithm>

namespace drone::safety {

enum class EvalResult : uint8_t {
    Ok = 0,
    HardTimeout,
    Stagnation,
    EkfDivergence,
    EnergyCritical
};

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr float distance_to(const Vector3f& other) const noexcept {
        const float dx = x - other.x;
        const float dy = y - other.y;
        const float dz = z - other.z;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }
};

struct BehaviorParams {
    std::chrono::microseconds hard_limit{std::chrono::seconds(60)};
    std::chrono::microseconds stagnation_time{std::chrono::seconds(6)};
    float min_speed_mps{0.35f};
    float max_pos_variance_m2{3.0f};
    float cruise_power_w{450.0f};
    float cruise_speed_mps{14.0f};
    float energy_margin_j{18000.0f};
};

struct BehaviorState {
    std::chrono::microseconds start_time{0};
    std::chrono::microseconds last_progress{0};
    Vector3f target_pos{};
    float min_distance_recorded_m{1e6f};
    uint8_t retry_count{0};
    bool is_active{false};
};

class BehaviorSafetyEvaluator {
public:
    explicit constexpr BehaviorSafetyEvaluator(const BehaviorParams& params) noexcept
        : params_(params) {}

    [[nodiscard]] EvalResult evaluate(BehaviorState& state,
                                      std::chrono::microseconds now,
                                      const Vector3f& curr_pos,
                                      const Vector3f& curr_vel,
                                      float ekf_variance_m2,
                                      float remaining_energy_j,
                                      const Vector3f& home_pos) const noexcept {
        if (!state.is_active) {
            return EvalResult::Ok;
        }

        // 1. Жорсткий дедлайн за монотонним таймером
        if ((now - state.start_time) >= params_.hard_limit) {
            return EvalResult::HardTimeout;
        }

        // 2. Дисперсія EKF
        if (ekf_variance_m2 > params_.max_pos_variance_m2) {
            return EvalResult::EkfDivergence;
        }

        // 3. Динамічний енергетичний бар'єр повернення
        const float dist_home = curr_pos.distance_to(home_pos);
        const float time_to_home_s = dist_home / std::max(params_.cruise_speed_mps, 1.0f);
        const float energy_needed_for_rtl_j = time_to_home_s * params_.cruise_power_w;

        if (remaining_energy_j <= (energy_needed_for_rtl_j + params_.energy_margin_j)) {
            return EvalResult::EnergyCritical;
        }

        // 4. Кінематичний прогрес наближення
        const float current_dist = curr_pos.distance_to(state.target_pos);

        if (current_dist < (state.min_distance_recorded_m - 0.25f)) {
            state.min_distance_recorded_m = current_dist;
            state.last_progress = now;
        } else if (current_dist > 1e-4f) {
            const float ux = (state.target_pos.x - curr_pos.x) / current_dist;
            const float uy = (state.target_pos.y - curr_pos.y) / current_dist;
            const float uz = (state.target_pos.z - curr_pos.z) / current_dist;
            const float v_proj = curr_vel.x * ux + curr_vel.y * uy + curr_vel.z * uz;

            if (v_proj >= params_.min_speed_mps) {
                state.last_progress = now;
            }
        }

        if ((now - state.last_progress) >= params_.stagnation_time) {
            return EvalResult::Stagnation;
        }

        return EvalResult::Ok;
    }

private:
    BehaviorParams params_;
};

} // namespace drone::safety
