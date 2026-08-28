#include <cmath>
#include <cstdint>
#include <optional>
#include <numbers>
#include <algorithm>

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
};

struct AngularError {
    float yaw_rad{0.0f};
    float pitch_rad{0.0f};
};

struct GimbalRateCommand {
    float yaw_rate_rad_s{0.0f};
    float pitch_rate_rad_s{0.0f};
};

class VisualServoController {
public:
    explicit VisualServoController(CameraIntrinsics intrinsics, float kp = 3.5f, float kd = 0.08f)
        : cam_(intrinsics), kp_(kp), kd_(kd) {}

    [[nodiscard]] std::optional<AngularError> computeErrors(const TargetBoundingBox& bbox) const noexcept {
        if (bbox.confidence < 0.5f) {
            return std::nullopt;
        }

        const float delta_u = bbox.u - cam_.cx;
        const float delta_v = bbox.v - cam_.cy;

        return AngularError{
            .yaw_rad = std::atan2(delta_u, cam_.fx),
            .pitch_rad = std::atan2(delta_v, cam_.fy)
        };
    }

    [[nodiscard]] GimbalRateCommand updateRates(const AngularError& err,
                                               float dt,
                                               float drone_gyro_yaw = 0.0f,
                                               float drone_gyro_pitch = 0.0f) noexcept {
        const float valid_dt = (dt > 0.0001f) ? dt : 0.0333f;

        const float d_yaw = (err.yaw_rad - prev_err_.yaw_rad) / valid_dt;
        const float d_pitch = (err.pitch_rad - prev_err_.pitch_rad) / valid_dt;
        prev_err_ = err;

        return GimbalRateCommand{
            .yaw_rate_rad_s = (kp_ * err.yaw_rad + kd_ * d_yaw) - drone_gyro_yaw,
            .pitch_rate_rad_s = (kp_ * err.pitch_rad + kd_ * d_pitch) - drone_gyro_pitch
        };
    }

    void reset() noexcept {
        prev_err_ = AngularError{};
    }

private:
    CameraIntrinsics cam_;
    float kp_{3.5f};
    float kd_{0.08f};
    AngularError prev_err_{};
};
