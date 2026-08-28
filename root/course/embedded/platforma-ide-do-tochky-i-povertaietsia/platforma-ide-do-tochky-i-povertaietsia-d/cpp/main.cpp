#include <algorithm>
#include <array>
#include <cmath>
#include <numbers>
#include <span>
#include <utility>

enum class NavState : uint8_t {
    Idle = 0,
    RotateToWaypoint,
    TrackWaypoint,
    ActionAtWaypoint,
    ReturnToBase,
    ParkedHome,
    FaultStall
};

struct Pose2D {
    float x{0.0f};     // Координата X, м
    float y{0.0f};     // Координата Y, м
    float theta{0.0f}; // Орієнтація, рад [-π, π]
};

struct Waypoint {
    float x{0.0f};
    float y{0.0f};
    float dwell_time_sec{0.0f};
};

struct NavConfig {
    float track_width_m{0.180f};
    float wheel_radius_m{0.0325f};
    float ticks_per_rev{1440.0f};
    float max_linear_vel{0.40f};
    float max_angular_vel{1.80f};
    float lookahead_dist{0.35f};
    float acceptance_rad{0.05f};
    float gyro_weight{0.96f};
};

class DifferentialNavigator {
public:
    static constexpr size_t MaxWaypoints = 16;

    explicit constexpr DifferentialNavigator(const NavConfig& config) noexcept
        : cfg_{config} {}

    [[nodiscard]] constexpr const Pose2D& pose() const noexcept { return pose_; }
    [[nodiscard]] constexpr NavState state() const noexcept { return state_; }
    [[nodiscard]] constexpr std::pair<float, float> wheel_speeds() const noexcept {
        return {wheel_vel_l_, wheel_vel_r_};
    }

    bool add_waypoint(const Waypoint& wp) noexcept {
        if (mission_count_ >= MaxWaypoints) return false;
        mission_[mission_count_++] = wp;
        return true;
    }

    void start_mission() noexcept {
        if (mission_count_ > 0) {
            current_wp_idx_ = 0;
            state_ = NavState::RotateToWaypoint;
        }
    }

    void set_gyro_bias(float bias_z) noexcept {
        gyro_bias_z_ = bias_z;
    }

    void update_odometry_imu(int32_t delta_ticks_l,
                             int32_t delta_ticks_r,
                             float gyro_z_rad_s,
                             float dt_sec) noexcept {
        constexpr float two_pi = 2.0f * std::numbers::pi_v<float>;
        const float c_tick = (two_pi * cfg_.wheel_radius_m) / cfg_.ticks_per_rev;

        const float ds_l = static_cast<float>(delta_ticks_l) * c_tick;
        const float ds_r = static_cast<float>(delta_ticks_r) * c_tick;

        const float ds = (ds_r + ds_l) * 0.5f;
        const float dtheta_odo = (ds_r - ds_l) / cfg_.track_width_m;

        const float gyro_clean = gyro_z_rad_s - gyro_bias_z_;
        const float dtheta_gyro = gyro_clean * dt_sec;

        const float dtheta_fused = (cfg_.gyro_weight * dtheta_gyro) +
                                   ((1.0f - cfg_.gyro_weight) * dtheta_odo);

        const float theta_mid = pose_.theta + (dtheta_fused * 0.5f);
        pose_.x += ds * std::cos(theta_mid);
        pose_.y += ds * std::sin(theta_mid);
        pose_.theta = wrap_to_pi(pose_.theta + dtheta_fused);
    }

    void step_fsm(float dt_sec) noexcept {
        float target_x = 0.0f;
        float target_y = 0.0f;

        switch (state_) {
            case NavState::Idle:
                cmd_linear_ = 0.0f;
                cmd_angular_ = 0.0f;
                break;

            case NavState::RotateToWaypoint: {
                const auto& wp = mission_[current_wp_idx_];
                const float target_azimuth = std::atan2(wp.y - pose_.y, wp.x - pose_.x);
                const float heading_err = wrap_to_pi(target_azimuth - pose_.theta);

                if (std::abs(heading_err) < 0.15f) {
                    state_ = NavState::TrackWaypoint;
                } else {
                    cmd_linear_ = 0.0f;
                    cmd_angular_ = std::clamp(1.8f * heading_err,
                                              -cfg_.max_angular_vel,
                                              cfg_.max_angular_vel);
                }
                break;
            }

            case NavState::TrackWaypoint: {
                const auto& wp = mission_[current_wp_idx_];
                const float dx = wp.x - pose_.x;
                const float dy = wp.y - pose_.y;
                const float dist = std::hypot(dx, dy);

                if (dist <= cfg_.acceptance_rad) {
                    cmd_linear_ = 0.0f;
                    cmd_angular_ = 0.0f;
                    action_timer_sec_ = wp.dwell_time_sec;
                    state_ = NavState::ActionAtWaypoint;
                } else {
                    compute_pure_pursuit(wp.x, wp.y);
                }
                break;
            }

            case NavState::ActionAtWaypoint:
                cmd_linear_ = 0.0f;
                cmd_angular_ = 0.0f;
                action_timer_sec_ -= dt_sec;

                if (action_timer_sec_ <= 0.0f) {
                    ++current_wp_idx_;
                    if (current_wp_idx_ >= mission_count_) {
                        state_ = NavState::ReturnToBase;
                    } else {
                        state_ = NavState::RotateToWaypoint;
                    }
                }
                break;

            case NavState::ReturnToBase: {
                const float dist = std::hypot(-pose_.x, -pose_.y);
                if (dist <= cfg_.acceptance_rad) {
                    state_ = NavState::ParkedHome;
                } else {
                    compute_pure_pursuit(0.0f, 0.0f);
                }
                break;
            }

            case NavState::ParkedHome: {
                const float home_err = wrap_to_pi(0.0f - pose_.theta);
                if (std::abs(home_err) < 0.05f) {
                    cmd_linear_ = 0.0f;
                    cmd_angular_ = 0.0f;
                    state_ = NavState::Idle;
                } else {
                    cmd_linear_ = 0.0f;
                    cmd_angular_ = std::clamp(1.5f * home_err,
                                              -cfg_.max_angular_vel,
                                              cfg_.max_angular_vel);
                }
                break;
            }

            default:
                cmd_linear_ = 0.0f;
                cmd_angular_ = 0.0f;
                break;
        }

        // Інверсна кінематика та масштабування швидкостей
        float v_l = cmd_linear_ - (cmd_angular_ * cfg_.track_width_m * 0.5f);
        float v_r = cmd_linear_ + (cmd_angular_ * cfg_.track_width_m * 0.5f);

        const float max_req = std::max(std::abs(v_l), std::abs(v_r));
        if (max_req > cfg_.max_linear_vel && max_req > 1e-4f) {
            const float scale = cfg_.max_linear_vel / max_req;
            v_l *= scale;
            v_r *= scale;
        }

        wheel_vel_l_ = v_l;
        wheel_vel_r_ = v_r;
    }

private:
    static constexpr float wrap_to_pi(float a) noexcept {
        constexpr float pi = std::numbers::pi_v<float>;
        constexpr float two_pi = 2.0f * pi;
        while (a > pi)  a -= two_pi;
        while (a < -pi) a += two_pi;
        return a;
    }

    void compute_pure_pursuit(float gx, float gy) noexcept {
        const float dx = gx - pose_.x;
        const float dy = gy - pose_.y;
        const float dist = std::hypot(dx, dy);

        if (dist < 0.001f) {
            cmd_linear_ = 0.0f;
            cmd_angular_ = 0.0f;
            return;
        }

        const float target_azimuth = std::atan2(dy, dx);
        const float heading_err = wrap_to_pi(target_azimuth - pose_.theta);

        const float d_slow = cfg_.lookahead_dist * 2.0f;
        const float dist_scale = std::clamp(dist / d_slow, 0.15f, 1.0f);
        const float angle_factor = std::max(0.0f, std::cos(heading_err));

        cmd_linear_ = cfg_.max_linear_vel * dist_scale * angle_factor;

        const float curvature = (2.0f * std::sin(heading_err)) / cfg_.lookahead_dist;
        cmd_angular_ = std::clamp(cmd_linear_ * curvature,
                                  -cfg_.max_angular_vel,
                                  cfg_.max_angular_vel);
    }

    NavConfig cfg_;
    Pose2D    pose_{};
    NavState  state_{NavState::Idle};

    std::array<Waypoint, MaxWaypoints> mission_{};
    size_t mission_count_{0};
    size_t current_wp_idx_{0};

    float action_timer_sec_{0.0f};
    float gyro_bias_z_{0.0f};

    float cmd_linear_{0.0f};
    float cmd_angular_{0.0f};
    float wheel_vel_l_{0.0f};
    float wheel_vel_r_{0.0f};
};
