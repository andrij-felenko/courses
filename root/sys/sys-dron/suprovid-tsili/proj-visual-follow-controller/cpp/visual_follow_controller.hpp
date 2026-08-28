// ============================================================================
// visual_follow_controller.hpp - Modern C++20 Implementation
// ============================================================================
#pragma once

#include <cmath>
#include <cstdint>
#include <optional>
#include <numbers>
#include <array>
#include <span>
#include <algorithm>

namespace vfc {

struct CameraIntrinsics {
    float fx{1000.0f};
    float fy{1000.0f};
    float cx{960.0f};
    float cy{540.0f};
};

struct TargetBoundingBox {
    float u{0.0f};
    float v{0.0f};
    float width{0.0f};
    float height{0.0f};
    float confidence{0.0f};
    uint32_t target_id{0};
    uint64_t timestamp_us{0};
};

struct DroneState {
    float pos_n{0.0f};
    float pos_e{0.0f};
    float pos_d{0.0f};
    float vel_n{0.0f};
    float vel_e{0.0f};
    float vel_d{0.0f};
    float roll_rad{0.0f};
    float pitch_rad{0.0f};
    float yaw_rad{0.0f};
    float gyro_yaw_rad_s{0.0f};
    float gyro_pitch_rad_s{0.0f};
};

struct GimbalPidConfig {
    float kp{3.5f};
    float kd{0.08f};
    float tau_d{0.015f};
    float max_rate_rad_s{2.5f};
    float min_pitch_rad{-1.48f}; // -85 deg
    float max_pitch_rad{0.35f};  // +20 deg
};

struct TrajectoryConfig {
    float follow_distance_m{25.0f};
    float follow_altitude_m{30.0f};
    float relative_angle_rad{std::numbers::pi_v<float>};
    float orbit_radius_m{35.0f};
    float orbit_speed_m_s{8.0f};
    float kp_pos{0.45f};
    float kp_pos_z{0.60f};
    float max_vel_horiz_m_s{20.0f};
    float max_vel_vert_m_s{4.0f};
};

struct ControlOutputs {
    float gimbal_yaw_rate_rad_s{0.0f};
    float gimbal_pitch_rate_rad_s{0.0f};
    float cmd_vel_n{0.0f};
    float cmd_vel_e{0.0f};
    float cmd_vel_d{0.0f};
    float cmd_acc_n{0.0f};
    float cmd_acc_e{0.0f};
    float cmd_acc_d{0.0f};
    float cmd_yaw_rad{0.0f};
    float cmd_yaw_rate_rad_s{0.0f};
    bool target_valid{false};
    bool occluded{false};
};

class alignas(64) VisualFollowController {
public:
    explicit VisualFollowController(CameraIntrinsics cam,
                                   GimbalPidConfig gimbal_cfg = {},
                                   TrajectoryConfig traj_cfg = {})
        : cam_(cam), gimbal_cfg_(gimbal_cfg), traj_cfg_(traj_cfg) {
        reset();
    }

    void reset() noexcept {
        x_.fill(0.0f);
        P_.fill(0.0f);
        for (std::size_t i = 0; i < 3; ++i) {
            P_[i * 6 + i] = 100.0f;
            P_[(i + 3) * 6 + (i + 3)] = 25.0f;
        }
        prev_err_yaw_ = 0.0f;
        prev_err_pitch_ = 0.0f;
        prev_d_err_yaw_ = 0.0f;
        prev_d_err_pitch_ = 0.0f;
        orbit_angle_rad_ = 0.0f;
        lost_frames_count_ = 0;
        is_initialized_ = false;
    }

    void predictKalman(float dt) noexcept {
        if (dt <= 0.0001f) return;

        // X = F * X
        x_[0] += x_[3] * dt;
        x_[1] += x_[4] * dt;
        x_[2] += x_[5] * dt;

        // P = F * P * F^T + Q
        const float dt2 = dt * dt;
        const float dt3_3 = (dt2 * dt) / 3.0f;
        const float dt2_2 = dt2 / 2.0f;
        const float q = q_acc_;

        for (std::size_t i = 0; i < 3; ++i) {
            const std::size_t v_idx = i + 3;
            P_[i * 6 + i] += dt * (P_[v_idx * 6 + i] + P_[i * 6 + v_idx]) + dt2 * P_[v_idx * 6 + v_idx] + dt3_3 * q;
            P_[i * 6 + v_idx] += dt * P_[v_idx * 6 + v_idx] + dt2_2 * q;
            P_[v_idx * 6 + i] += dt * P_[v_idx * 6 + v_idx] + dt2_2 * q;
            P_[v_idx * 6 + v_idx] += dt * q;
        }
    }

    bool updateKalman(const DroneState& drone,
                      const TargetBoundingBox& bbox,
                      float terrain_alt_m = 0.0f) noexcept {
        if (bbox.confidence < 0.5f) {
            ++lost_frames_count_;
            return false;
        }

        const float delta_u = bbox.u - cam_.cx;
        const float delta_v = bbox.v - cam_.cy;
        const float norm = std::sqrt(delta_u * delta_u / (cam_.fx * cam_.fx) +
                                     delta_v * delta_v / (cam_.fy * cam_.fy) + 1.0f);
        
        const float los_c_x = (delta_u / cam_.fx) / norm;
        const float los_c_y = (delta_v / cam_.fy) / norm;
        const float los_c_z = 1.0f / norm;

        const float cy = std::cos(drone.yaw_rad);
        const float sy = std::sin(drone.yaw_rad);
        const float cp = std::cos(drone.pitch_rad);
        const float sp = std::sin(drone.pitch_rad);
        const float cr = std::cos(drone.roll_rad);
        const float sr = std::sin(drone.roll_rad);

        const float r33 = cp * cr;
        const float los_ned_d = r33 * los_c_z + (-sp) * los_c_x + (cp * sr) * los_c_y;

        if (std::abs(los_ned_d) < 0.05f) {
            return false;
        }

        float height_agl = terrain_alt_m - drone.pos_d;
        if (height_agl <= 1.0f) height_agl = 1.0f;

        const float slant_range = height_agl / los_ned_d;
        if (slant_range <= 0.0f || slant_range > 1500.0f) {
            return false;
        }

        const std::array<float, 3> z_meas{
            drone.pos_n + (cy * cp) * (slant_range * los_c_z),
            drone.pos_e + (sy * cp) * (slant_range * los_c_z),
            drone.pos_d + los_ned_d * slant_range
        };

        if (!is_initialized_) {
            x_[0] = z_meas[0];
            x_[1] = z_meas[1];
            x_[2] = z_meas[2];
            x_[3] = 0.0f;
            x_[4] = 0.0f;
            x_[5] = 0.0f;
            is_initialized_ = true;
            lost_frames_count_ = 0;
            return true;
        }

        std::array<float, 3> y_res{};
        std::array<float, 3> S{};
        float d_mahalanobis_sq = 0.0f;

        for (std::size_t i = 0; i < 3; ++i) {
            y_res[i] = z_meas[i] - x_[i];
            S[i] = P_[i * 6 + i] + r_pos_;
            d_mahalanobis_sq += (y_res[i] * y_res[i]) / S[i];
        }

        if (d_mahalanobis_sq > 11.34f) {
            ++lost_frames_count_;
            return false;
        }

        for (std::size_t i = 0; i < 3; ++i) {
            const std::size_t v_idx = i + 3;
            const float K_pos = P_[i * 6 + i] / S[i];
            const float K_vel = P_[v_idx * 6 + i] / S[i];

            x_[i] += K_pos * y_res[i];
            x_[v_idx] += K_vel * y_res[i];

            P_[i * 6 + i] = (1.0f - K_pos) * P_[i * 6 + i];
            P_[v_idx * 6 + i] = (1.0f - K_pos) * P_[v_idx * 6 + i];
            P_[i * 6 + v_idx] = P_[v_idx * 6 + i];
            P_[v_idx * 6 + v_idx] -= K_vel * P_[i * 6 + v_idx];
        }

        lost_frames_count_ = 0;
        return true;
    }

    [[nodiscard]] ControlOutputs update(const DroneState& drone,
                                        std::optional<TargetBoundingBox> bbox,
                                        bool orbit_mode,
                                        float dt) noexcept {
        const float valid_dt = (dt > 0.0001f) ? dt : 0.02f;
        ControlOutputs out{};

        predictKalman(valid_dt);
        if (bbox && bbox->confidence >= 0.5f) {
            updateKalman(drone, *bbox);
        }

        out.target_valid = is_initialized_ && (lost_frames_count_ < 150);
        out.occluded = (lost_frames_count_ > 3);

        if (bbox && bbox->confidence >= 0.5f) {
            const float delta_u = bbox->u - cam_.cx;
            const float delta_v = bbox->v - cam_.cy;

            const float err_yaw = std::atan2(delta_u, cam_.fx);
            const float err_pitch = std::atan2(delta_v, cam_.fy);

            const float d_err_yaw_raw = (err_yaw - prev_err_yaw_) / valid_dt;
            const float d_err_pitch_raw = (err_pitch - prev_err_pitch_) / valid_dt;

            const float alpha = valid_dt / (valid_dt + gimbal_cfg_.tau_d);
            const float d_err_yaw = alpha * d_err_yaw_raw + (1.0f - alpha) * prev_d_err_yaw_;
            const float d_err_pitch = alpha * d_err_pitch_raw + (1.0f - alpha) * prev_d_err_pitch_;

            prev_err_yaw_ = err_yaw;
            prev_err_pitch_ = err_pitch;
            prev_d_err_yaw_ = d_err_yaw;
            prev_d_err_pitch_ = d_err_pitch;

            const float cmd_yaw_rate = (gimbal_cfg_.kp * err_yaw + gimbal_cfg_.kd * d_err_yaw) - drone.gyro_yaw_rad_s;
            const float cmd_pitch_rate = (gimbal_cfg_.kp * err_pitch + gimbal_cfg_.kd * d_err_pitch) - drone.gyro_pitch_rad_s;

            out.gimbal_yaw_rate_rad_s = std::clamp(cmd_yaw_rate, -gimbal_cfg_.max_rate_rad_s, gimbal_cfg_.max_rate_rad_s);
            out.gimbal_pitch_rate_rad_s = std::clamp(cmd_pitch_rate, -gimbal_cfg_.max_rate_rad_s, gimbal_cfg_.max_rate_rad_s);
        }

        if (out.target_valid) {
            float pos_sp_n = 0.0f;
            float pos_sp_e = 0.0f;
            const float pos_sp_d = x_[2] - traj_cfg_.follow_altitude_m;

            float vel_ff_n = x_[3];
            float vel_ff_e = x_[4];
            const float vel_ff_d = x_[5];

            if (!orbit_mode) {
                const float tgt_heading = std::atan2(x_[4], x_[3]);
                const float drone_azimuth = tgt_heading + traj_cfg_.relative_angle_rad;

                pos_sp_n = x_[0] - traj_cfg_.follow_distance_m * std::cos(drone_azimuth);
                pos_sp_e = x_[1] - traj_cfg_.follow_distance_m * sinf(drone_azimuth);
            } else {
                const float omega_orbit = traj_cfg_.orbit_speed_m_s / traj_cfg_.orbit_radius_m;
                orbit_angle_rad_ += omega_orbit * valid_dt;
                if (orbit_angle_rad_ > 2.0f * std::numbers::pi_v<float>) {
                    orbit_angle_rad_ -= 2.0f * std::numbers::pi_v<float>;
                }

                pos_sp_n = x_[0] + traj_cfg_.orbit_radius_m * std::cos(orbit_angle_rad_);
                pos_sp_e = x_[1] + traj_cfg_.orbit_radius_m * sinf(orbit_angle_rad_);

                vel_ff_n += -traj_cfg_.orbit_speed_m_s * std::sin(orbit_angle_rad_);
                vel_ff_e +=  traj_cfg_.orbit_speed_m_s * std::cos(orbit_angle_rad_);

                const float a_centripetal = (traj_cfg_.orbit_speed_m_s * traj_cfg_.orbit_speed_m_s) / traj_cfg_.orbit_radius_m;
                out.cmd_acc_n = -a_centripetal * std::cos(orbit_angle_rad_);
                out.cmd_acc_e = -a_centripetal * sinf(orbit_angle_rad_);
            }

            const float err_pos_n = pos_sp_n - drone.pos_n;
            const float err_pos_e = pos_sp_e - drone.pos_e;
            const float err_pos_d = pos_sp_d - drone.pos_d;

            out.cmd_vel_n = std::clamp(vel_ff_n + traj_cfg_.kp_pos * err_pos_n, -traj_cfg_.max_vel_horiz_m_s, traj_cfg_.max_vel_horiz_m_s);
            out.cmd_vel_e = std::clamp(vel_ff_e + traj_cfg_.kp_pos * err_pos_e, -traj_cfg_.max_vel_horiz_m_s, traj_cfg_.max_vel_horiz_m_s);
            out.cmd_vel_d = std::clamp(vel_ff_d + traj_cfg_.kp_pos_z * err_pos_d, -traj_cfg_.max_vel_vert_m_s, traj_cfg_.max_vel_vert_m_s);

            out.cmd_yaw_rad = std::atan2(x_[1] - drone.pos_e, x_[0] - drone.pos_n);
            if (orbit_mode) {
                out.cmd_yaw_rate_rad_s = traj_cfg_.orbit_speed_m_s / traj_cfg_.orbit_radius_m;
            }
        }

        return out;
    }

private:
    CameraIntrinsics cam_;
    GimbalPidConfig gimbal_cfg_;
    TrajectoryConfig traj_cfg_;

    alignas(64) std::array<float, 6> x_{};
    alignas(64) std::array<float, 36> P_{};
    float q_acc_{3.0f};
    float r_pos_{0.25f};

    float prev_err_yaw_{0.0f};
    float prev_err_pitch_{0.0f};
    float prev_d_err_yaw_{0.0f};
    float prev_d_err_pitch_{0.0f};
    float orbit_angle_rad_{0.0f};
    uint32_t lost_frames_count_{0};
    bool is_initialized_{false};
};

} // namespace vfc
