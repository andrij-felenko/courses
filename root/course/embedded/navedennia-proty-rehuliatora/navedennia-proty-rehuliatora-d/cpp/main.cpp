/* ============================================================================
   Модуль розділення Наведення (Guidance) та Регулювання (Control)
   Мова: C++20 з типобезпекою, атомарним обміном та RAII-структурою
   ============================================================================ */

#include <cmath>
#include <cstdint>
#include <array>
#include <atomic>
#include <numbers>
#include <optional>

namespace FlightCore {

/* Строго типізований тривимірний вектор */
struct Vector3 {
    float x{0.0f}, y{0.0f}, z{0.0f};

    [[nodiscard]] constexpr float norm_sq() const noexcept {
        return x * x + y * y + z * z;
    }

    [[nodiscard]] float norm() const noexcept {
        return std::sqrt(norm_sq());
    }

    [[nodiscard]] Vector3 normalized() const noexcept {
        const float n = norm();
        if (n < 1e-6f) return {0.0f, 0.0f, -1.0f};
        return {x / n, y / n, z / n};
    }
};

/* Кватерніон просторової орієнтації */
struct Quaternion {
    float w{1.0f}, x{0.0f}, y{0.0f}, z{0.0f};

    [[nodiscard]] constexpr Quaternion conjugate() const noexcept {
        return {w, -x, -y, -z};
    }

    [[nodiscard]] constexpr Quaternion operator*(const Quaternion& rhs) const noexcept {
        return {
            w * rhs.w - x * rhs.x - y * rhs.y - z * rhs.z,
            w * rhs.x + x * rhs.w + y * rhs.z - z * rhs.y,
            w * rhs.y - x * rhs.z + y * rhs.w + z * rhs.x,
            w * rhs.z + x * rhs.y - y * rhs.x + z * rhs.w
        };
    }
};

/* Контрактний інтерфейс уставки між доменами */
struct SetpointPayload {
    uint64_t timestamp_us{0};
    Quaternion q_target{1.0f, 0.0f, 0.0f, 0.0f};
    Vector3 rate_feedforward{};
    float collective_thrust{0.0f};
    bool valid{false};
};

/* Потокобезпечна безблокувальна поштова скринька (Lock-Free Mailbox) */
class SetpointMailbox {
public:
    void publish(const SetpointPayload& sp) noexcept {
        const uint32_t current_seq = m_sequence.load(std::memory_order_relaxed);
        const uint32_t next_idx = (current_seq & 1) ^ 1;
        
        m_buffers[next_idx] = sp;
        
        /* Звільняємо пам'ять із бар'єром release */
        m_sequence.store(current_seq + 1, std::memory_order_release);
    }

    [[nodiscard]] std::optional<SetpointPayload> consume() const noexcept {
        const uint32_t seq = m_sequence.load(std::memory_order_acquire);
        const uint32_t read_idx = seq & 1;
        
        SetpointPayload sp = m_buffers[read_idx];
        
        if (m_sequence.load(std::memory_order_relaxed) != seq || !sp.valid) {
            return std::nullopt;
        }
        return sp;
    }

private:
    std::array<SetpointPayload, 2> m_buffers{};
    std::atomic<uint32_t> m_sequence{0};
};

/* ----------------------------------------------------------------------------
   Клас контуру наведення (Guidance Controller, 20–50 Гц)
   ---------------------------------------------------------------------------- */
class GuidanceSystem {
public:
    static constexpr float MAX_TILT_RAD = 0.610865f; /* 35 градусів */
    static constexpr float GRAVITY_MSS  = 9.80665f;

    [[nodiscard]] SetpointPayload compute_setpoint(const Vector3& a_des_ned, 
                                                  float yaw_target_rad, 
                                                  uint64_t now_us) const noexcept 
    {
        SetpointPayload sp{};
        sp.timestamp_us = now_us;

        /* Розрахунок питомої сили f = a_des - g */
        Vector3 f_des{a_des_ned.x, a_des_ned.y, a_des_ned.z - GRAVITY_MSS};
        const float f_norm = f_des.norm();

        Vector3 zb = (f_des * (-1.0f)).normalized();

        /* Tilt Limiter */
        const float min_zb_z = std::cos(MAX_TILT_RAD);
        if (zb.z < min_zb_z) {
            const float xy_len = std::sqrt(zb.x * zb.x + zb.y * zb.y);
            if (xy_len > 1e-4f) {
                const float sin_max = std::sin(MAX_TILT_RAD);
                zb.x = (zb.x / xy_len) * sin_max;
                zb.y = (zb.y / xy_len) * sin_max;
                zb.z = min_zb_z;
            }
        }

        /* Генерація кватерніона за кутами Ейлера */
        const float pitch = std::asin(-zb.x);
        const float roll  = std::atan2(zb.y, zb.z);

        const float cy = std::cos(yaw_target_rad * 0.5f);
        const float sy = std::sin(yaw_target_rad * 0.5f);
        const float cp = std::cos(pitch * 0.5f);
        const float sp_val = std::sin(pitch * 0.5f);
        const float cr = std::cos(roll * 0.5f);
        const float sr = std::sin(roll * 0.5f);

        sp.q_target = Quaternion{
            cr * cp * cy + sr * sp_val * sy,
            sr * cp * cy - cr * sp_val * sy,
            cr * sp_val * cy + sr * cp * sy,
            cr * cp * sy - sr * sp_val * cy
        };

        /* Розрахунок тяги з насиченням */
        sp.collective_thrust = std::clamp(f_norm / (2.0f * GRAVITY_MSS), 0.05f, 1.0f);
        sp.valid = true;

        return sp;
    }
};

/* ----------------------------------------------------------------------------
   Клас контуру стабілізації (Attitude Rate Controller, 1000 Гц)
   ---------------------------------------------------------------------------- */
class RateController {
public:
    static constexpr uint64_t TIMEOUT_US = 100'000; /* 100 мс */
    static constexpr float KP_ATTITUDE = 6.5f;
    static constexpr float KP_RATE = 0.15f;

    struct ActuatorCommands {
        Vector3 body_torques{};
        float thrust{0.0f};
    };

    [[nodiscard]] ActuatorCommands update(const Quaternion& q_est, 
                                          const Vector3& gyro_rad_s,
                                          const std::optional<SetpointPayload>& sp_opt,
                                          uint64_t now_us) noexcept 
    {
        SetpointPayload sp = resolve_watchdog(sp_opt, now_us);

        /* 1. Похибка орієнтації в системі Body: q_err = q_est* * q_target */
        const Quaternion q_err = q_est.conjugate() * sp.q_target;
        const float sign = (q_err.w >= 0.0f) ? 1.0f : -1.0f;

        /* Цільова кутова швидкість */
        const Vector3 rate_target{
            2.0f * sign * q_err.x * KP_ATTITUDE + sp.rate_feedforward.x,
            2.0f * sign * q_err.y * KP_ATTITUDE + sp.rate_feedforward.y,
            2.0f * sign * q_err.z * (KP_ATTITUDE * 0.6f) + sp.rate_feedforward.z
        };

        /* 2. Контур кутових швидкостей */
        const Vector3 rate_err{
            rate_target.x - gyro_rad_s.x,
            rate_target.y - gyro_rad_s.y,
            rate_target.z - gyro_rad_s.z
        };

        return ActuatorCommands{
            .body_torques = Vector3{
                rate_err.x * KP_RATE,
                rate_err.y * KP_RATE,
                rate_err.z * (KP_RATE * 1.5f)
            },
            .thrust = sp.collective_thrust
        };
    }

private:
    [[nodiscard]] SetpointPayload resolve_watchdog(const std::optional<SetpointPayload>& sp_opt,
                                                  uint64_t now_us) const noexcept 
    {
        if (!sp_opt.has_value() || (now_us - sp_opt->timestamp_us > TIMEOUT_US)) {
            /* Fallback: горизонтальний режим та спуск */
            return SetpointPayload{
                .timestamp_us = now_us,
                .q_target = Quaternion{1.0f, 0.0f, 0.0f, 0.0f},
                .rate_feedforward = {},
                .collective_thrust = 0.40f,
                .valid = true
            };
        }
        return *sp_opt;
    }
};

} // namespace FlightCore
