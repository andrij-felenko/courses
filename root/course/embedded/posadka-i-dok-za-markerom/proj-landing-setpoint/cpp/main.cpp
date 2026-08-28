#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <optional>

namespace precision_landing {

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr Vector3f operator+(const Vector3f& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vector3f operator-(const Vector3f& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vector3f operator*(float s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] float norm_xy() const noexcept {
        return std::sqrt(x * x + y * y);
    }
};

struct Config {
    float kp_xy{1.1f};
    float ki_xy{0.25f};
    float kd_xy{0.05f};
    float kp_z{0.45f};
    float i_limit_xy{0.6f};
    float cone_slope{0.45f};
    float min_cone_radius{0.06f};
    float max_horizontal_vel{1.5f};
    float max_vertical_vel{0.8f};
    float min_vertical_vel{0.15f};
    float marker_timeout_sec{0.4f};
    std::array<std::array<float, 3>, 3> cam_to_body_r{
        std::array<float, 3>{0.0f, 1.0f, 0.0f},
        std::array<float, 3>{1.0f, 0.0f, 0.0f},
        std::array<float, 3>{0.0f, 0.0f, 1.0f}
    };
    Vector3f cam_to_body_t{0.05f, 0.0f, 0.08f};
};

struct MarkerMeasurement {
    Vector3f pos_camera;
    float yaw_camera_rad{0.0f};
    uint32_t marker_id{0};
    Vector3f offset_in_dock_body{0.0f, 0.0f, 0.0f};
};

struct ControllerOutput {
    Vector3f vel_setpoint_body;
    float yaw_rate_setpoint{0.0f};
    bool descent_allowed{false};
    bool touchdown_ready{false};
};

class LandingGuidanceController {
public:
    explicit LandingGuidanceController(Config config) noexcept
        : cfg_(config) {}

    void reset() noexcept {
        integral_err_ = {0.0f, 0.0f, 0.0f};
        prev_body_err_ = {0.0f, 0.0f, 0.0f};
        last_detection_time_ = 0.0f;
        active_marker_id_ = 0;
        is_tracking_ = false;
    }

    [[nodiscard]] std::optional<ControllerOutput> update(
        const std::optional<MarkerMeasurement>& marker_meas,
        const Vector3f& current_body_vel,
        float latency_sec,
        float current_time_sec,
        float dt_sec) noexcept
    {
        if (dt_sec <= 0.0f || dt_sec > 0.2f) {
            return std::nullopt;
        }

        if (marker_meas.has_value()) {
            last_detection_time_ = current_time_sec;
            active_marker_id_ = marker_meas->marker_id;
            is_tracking_ = true;
        } else if (current_time_sec - last_detection_time_ > cfg_.marker_timeout_sec) {
            is_tracking_ = false;
            return std::nullopt;
        }

        Vector3f target_body{};
        float yaw_cam = 0.0f;

        if (marker_meas.has_value()) {
            Vector3f raw_body = transform_cam_to_body(marker_meas->pos_camera);
            raw_body.x -= marker_meas->offset_in_dock_body.x;
            raw_body.y -= marker_meas->offset_in_dock_body.y;

            target_body = raw_body - (current_body_vel * latency_sec);
            prev_body_err_ = target_body;
            yaw_cam = marker_meas->yaw_camera_rad;
        } else {
            target_body = prev_body_err_ - (current_body_vel * dt_sec);
            prev_body_err_ = target_body;
        }

        const float err_x = target_body.x;
        const float err_y = target_body.y;
        const float altitude = target_body.z;
        const float horiz_dist = std::sqrt(err_x * err_x + err_y * err_y);
        const float cone_radius = altitude * cfg_.cone_slope + cfg_.min_cone_radius;

        const bool inside_cone = (horiz_dist <= cone_radius);

        integral_err_.x = std::clamp(integral_err_.x + err_x * dt_sec,
                                     -cfg_.i_limit_xy, cfg_.i_limit_xy);
        integral_err_.y = std::clamp(integral_err_.y + err_y * dt_sec,
                                     -cfg_.i_limit_xy, cfg_.i_limit_xy);

        ControllerOutput out{};
        out.descent_allowed = inside_cone;

        const float cmd_vx = cfg_.kp_xy * err_x + cfg_.ki_xy * integral_err_.x;
        const float cmd_vy = cfg_.kp_xy * err_y + cfg_.ki_xy * integral_err_.y;

        out.vel_setpoint_body.x = std::clamp(cmd_vx, -cfg_.max_horizontal_vel, cfg_.max_horizontal_vel);
        out.vel_setpoint_body.y = std::clamp(cmd_vy, -cfg_.max_horizontal_vel, cfg_.max_horizontal_vel);

        if (inside_cone && altitude > 0.05f) {
            const float vz_cmd = cfg_.kp_z * altitude;
            out.vel_setpoint_body.z = std::clamp(vz_cmd, cfg_.min_vertical_vel, cfg_.max_vertical_vel);
        } else {
            out.vel_setpoint_body.z = 0.0f;
        }

        if (marker_meas.has_value()) {
            out.yaw_rate_setpoint = std::clamp(0.8f * yaw_cam, -0.5f, 0.5f);
        } else {
            out.yaw_rate_setpoint = 0.0f;
        }

        out.touchdown_ready = (altitude < 0.12f) && (horiz_dist < 0.04f);

        return out;
    }

    [[nodiscard]] bool is_tracking() const noexcept { return is_tracking_; }
    [[nodiscard]] uint32_t active_marker_id() const noexcept { return active_marker_id_; }

private:
    [[nodiscard]] Vector3f transform_cam_to_body(const Vector3f& v_cam) const noexcept {
        return {
            cfg_.cam_to_body_r[0][0] * v_cam.x + cfg_.cam_to_body_r[0][1] * v_cam.y +
            cfg_.cam_to_body_r[0][2] * v_cam.z + cfg_.cam_to_body_t.x,

            cfg_.cam_to_body_r[1][0] * v_cam.x + cfg_.cam_to_body_r[1][1] * v_cam.y +
            cfg_.cam_to_body_r[1][2] * v_cam.z + cfg_.cam_to_body_t.y,

            cfg_.cam_to_body_r[2][0] * v_cam.x + cfg_.cam_to_body_r[2][1] * v_cam.y +
            cfg_.cam_to_body_r[2][2] * v_cam.z + cfg_.cam_to_body_t.z
        };
    }

    Config cfg_;
    Vector3f integral_err_{0.0f, 0.0f, 0.0f};
    Vector3f prev_body_err_{0.0f, 0.0f, 0.0f};
    float last_detection_time_{0.0f};
    uint32_t active_marker_id_{0};
    bool is_tracking_{false};
};

} // namespace precision_landing
