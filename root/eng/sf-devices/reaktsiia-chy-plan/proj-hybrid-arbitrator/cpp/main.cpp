#include <atomic>
#include <cmath>
#include <array>
#include <optional>
#include <span>
#include <algorithm>

class HybridTrajectoryController {
public:
    enum class Mode : uint8_t {
        Idle,
        FollowingPlan,
        ReactiveOverride,
        BlendingRecovery
    };

    struct TrajectoryPoint {
        float position{0.0f};
        float velocity{0.0f};
        float acceleration{0.0f};
    };

    explicit HybridTrajectoryController(float safe_distance = 0.30f, 
                                       float max_emergency_decel = 15.0f,
                                       float blend_duration = 0.20f) noexcept
        : safe_distance_m_(safe_distance),
          max_decel_emergency_(max_emergency_decel),
          blend_duration_s_(blend_duration) {}

    // ── Повільний шар (Slow Path): передача нової точки фоновим планувальником
    void submit_planned_setpoint(const TrajectoryPoint& pt) noexcept {
        const auto current_active = active_idx_.load(std::memory_order_relaxed);
        const auto write_idx = 1 - current_active;
        
        plan_buffer_[write_idx] = pt;
        active_idx_.store(write_idx, std::memory_order_release);
    }

    // Перевірка планувальником потреби у повному глобальному реплануванні
    [[nodiscard]] bool check_and_clear_replan_flag() noexcept {
        return replan_required_.exchange(false, std::memory_order_acq_rel);
    }

    // ── Швидкий шар (Fast Path): 1 кГц детерміністичний крок із ISR таймера ──
    [[nodiscard]] float process_control_step(float sensor_proximity_m, float dt = 0.001f) noexcept {
        const bool hazard = (sensor_proximity_m < safe_distance_m_);

        // 1. Миттєве виявлення загрози (Subsumption тригер)
        if (hazard && mode_ != Mode::ReactiveOverride) {
            mode_ = Mode::ReactiveOverride;
            replan_required_.store(true, std::memory_order_release);
        }

        // 2. Арбітраж і розрахунок команди на актуатор
        float output_velocity = 0.0f;

        switch (mode_) {
            case Mode::ReactiveOverride: {
                // Екстрене сповільнення до повної зупинки
                if (current_velocity_ > 0.0f) {
                    current_velocity_ = std::max(0.0f, current_velocity_ - max_decel_emergency_ * dt);
                } else if (current_velocity_ < 0.0f) {
                    current_velocity_ = std::min(0.0f, current_velocity_ + max_decel_emergency_ * dt);
                }

                current_position_ += current_velocity_ * dt;
                output_velocity = current_velocity_;

                // Коли загрозу знято і вісь зупинилась — починаємо злиття
                if (!hazard && std::abs(current_velocity_) < 0.005f) {
                    mode_ = Mode::BlendingRecovery;
                    blend_start_pos_ = current_position_;
                    blend_start_vel_ = current_velocity_;
                    blend_progress_ = 0.0f;
                }
                break;
            }

            case Mode::BlendingRecovery: {
                // Обчислення кубічного сплайна Ерміта C^1 (Bumpless Transfer)
                blend_progress_ += dt / blend_duration_s_;
                const auto active = active_idx_.load(std::memory_order_acquire);
                const auto& target = plan_buffer_[active];

                if (blend_progress_ >= 1.0f) {
                    mode_ = Mode::FollowingPlan;
                    current_position_ = target.position;
                    current_velocity_ = target.velocity;
                    output_velocity = target.velocity;
                } else {
                    const float s = blend_progress_;
                    const float s2 = s * s;
                    const float s3 = s2 * s;

                    const float h00 = 2.0f * s3 - 3.0f * s2 + 1.0f;
                    const float h10 = s3 - 2.0f * s2 + s;
                    const float h01 = -2.0f * s3 + 3.0f * s2;
                    const float h11 = s3 - s2;

                    const float blended_pos = h00 * blend_start_pos_ +
                                              h10 * blend_start_vel_ * blend_duration_s_ +
                                              h01 * target.position +
                                              h11 * target.velocity * blend_duration_s_;

                    output_velocity = (blended_pos - current_position_) / dt;
                    current_position_ = blended_pos;
                    current_velocity_ = output_velocity;
                }
                break;
            }

            case Mode::FollowingPlan:
            case Mode::Idle:
            default: {
                const auto active = active_idx_.load(std::memory_order_acquire);
                const auto& target = plan_buffer_[active];

                current_position_ = target.position;
                current_velocity_ = target.velocity;
                output_velocity = target.velocity;
                break;
            }
        }

        return output_velocity;
    }

    [[nodiscard]] Mode current_mode() const noexcept { return mode_; }
    [[nodiscard]] float current_position() const noexcept { return current_position_; }
    [[nodiscard]] float current_velocity() const noexcept { return current_velocity_; }

private:
    float safe_distance_m_;
    float max_decel_emergency_;
    float blend_duration_s_;

    float current_position_{0.0f};
    float current_velocity_{0.0f};

    Mode mode_{Mode::Idle};

    std::array<TrajectoryPoint, 2> plan_buffer_{};
    std::atomic<int> active_idx_{0};

    float blend_start_pos_{0.0f};
    float blend_start_vel_{0.0f};
    float blend_progress_{0.0f};

    std::atomic<bool> replan_required_{false};
};
