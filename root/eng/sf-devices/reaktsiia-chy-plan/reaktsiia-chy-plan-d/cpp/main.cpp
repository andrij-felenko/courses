#include <atomic>
#include <cmath>
#include <array>
#include <algorithm>

class HybridDecisionArbiter {
public:
    enum class Mode : uint8_t {
        FollowPlan,
        ReactiveOverride,
        BlendRecovery
    };

    struct TrajectoryPoint {
        float pos{0.0f};
        float vel{0.0f};
    };

    explicit HybridDecisionArbiter(float safe_distance = 0.25f, 
                                  float max_emergency_decel = 12.0f,
                                  float blend_duration = 0.15f) noexcept
        : safe_distance_m_(safe_distance),
          max_emergency_decel_(max_emergency_decel),
          blend_duration_s_(blend_duration) {}

    // ── Повільний шар: надсилання уставки планувальником (10–50 Гц) ───────────
    void push_planned_setpoint(float target_pos, float target_vel) noexcept {
        const auto active = active_slot_.load(std::memory_order_relaxed);
        const auto write_slot = 1 - active;

        plan_buffer_[write_slot] = TrajectoryPoint{target_pos, target_vel};
        active_slot_.store(write_slot, std::memory_order_release);
    }

    // Перевірка планувальником: чи потрібно перебудувати глобальний маршрут
    [[nodiscard]] bool check_and_clear_replan_event() noexcept {
        return replan_event_.exchange(false, std::memory_order_acq_rel);
    }

    // ── Швидкий шар: 1 кГц детерміністичний такт переривання ──────────────────
    [[nodiscard]] float process_fast_cycle(float distance_sensor_m, float dt = 0.001f) noexcept {
        const bool obstacle_near = (distance_sensor_m < safe_distance_m_);

        // 1. Реактивне перехоплення пріоритету
        if (obstacle_near && mode_ != Mode::ReactiveOverride) {
            mode_ = Mode::ReactiveOverride;
            replan_event_.store(true, std::memory_order_release);
        }

        float cmd_velocity = 0.0f;

        switch (mode_) {
            case Mode::ReactiveOverride: {
                // Аварійне гальмування
                if (actual_vel_ > 0.0f) {
                    actual_vel_ = std::max(0.0f, actual_vel_ - max_emergency_decel_ * dt);
                } else if (actual_vel_ < 0.0f) {
                    actual_vel_ = std::min(0.0f, actual_vel_ + max_emergency_decel_ * dt);
                }

                actual_pos_ += actual_vel_ * dt;
                cmd_velocity = actual_vel_;

                if (!obstacle_near && std::abs(actual_vel_) < 0.01f) {
                    mode_ = Mode::BlendRecovery;
                    blend_start_p_ = actual_pos_;
                    blend_start_v_ = actual_vel_;
                    blend_progress_ = 0.0f;
                }
                break;
            }

            case Mode::BlendRecovery: {
                // Злиття траєкторій за поліномом Ерміта
                blend_progress_ += dt / blend_duration_s_;
                const auto active = active_slot_.load(std::memory_order_acquire);
                const auto& target = plan_buffer_[active];

                if (blend_progress_ >= 1.0f) {
                    mode_ = Mode::FollowPlan;
                    actual_pos_ = target.pos;
                    actual_vel_ = target.vel;
                    cmd_velocity = target.vel;
                } else {
                    const float s = blend_progress_;
                    const float s2 = s * s;
                    const float s3 = s2 * s;

                    const float h00 = 2.0f * s3 - 3.0f * s2 + 1.0f;
                    const float h10 = s3 - 2.0f * s2 + s;
                    const float h01 = -2.0f * s3 + 3.0f * s2;
                    const float h11 = s3 - s2;

                    const float p_blend = h00 * blend_start_p_ +
                                          h10 * blend_start_v_ * blend_duration_s_ +
                                          h01 * target.pos +
                                          h11 * target.vel * blend_duration_s_;

                    cmd_velocity = (p_blend - actual_pos_) / dt;
                    actual_pos_ = p_blend;
                    actual_vel_ = cmd_velocity;
                }
                break;
            }

            case Mode::FollowPlan:
            default: {
                const auto active = active_slot_.load(std::memory_order_acquire);
                const auto& target = plan_buffer_[active];

                actual_pos_ = target.pos;
                actual_vel_ = target.vel;
                cmd_velocity = target.vel;
                break;
            }
        }

        return cmd_velocity;
    }

    [[nodiscard]] Mode current_mode() const noexcept { return mode_; }
    [[nodiscard]] float position() const noexcept { return actual_pos_; }
    [[nodiscard]] float velocity() const noexcept { return actual_vel_; }

private:
    float safe_distance_m_;
    float max_emergency_decel_;
    float blend_duration_s_;

    float actual_pos_{0.0f};
    float actual_vel_{0.0f};
    Mode mode_{Mode::FollowPlan};

    std::array<TrajectoryPoint, 2> plan_buffer_{};
    std::atomic<int> active_slot_{0};

    float blend_start_p_{0.0f};
    float blend_start_v_{0.0f};
    float blend_progress_{0.0f};

    std::atomic<bool> replan_event_{false};
};
