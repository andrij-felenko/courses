#include "attitude.hpp"

namespace nav {

void AttitudeEstimator::push_gyro(const Vector3& omega_body, float dt) noexcept {
    if (!omega_body.finite() || !(dt > 0.0F) || !std::isfinite(dt)) {
        ++faults_;   // битий кадр IMU не рухає стан: пропустити такт дешевше, ніж отруїти оцінку
        return;
    }
    const Vector3 step = (omega_body - bias_) * dt;
    if (coning_enabled_ && fast_steps_ > 0) {
        // Δθ_coning = 0.5·(Δθ_{k−1} × Δθ_k): те, що втрачає просте підсумовування.
        coning_ += prev_delta_.cross(step) * 0.5F;
    }
    prev_delta_ = step;
    delta_theta_ += step;
    ++fast_steps_;
}

void AttitudeEstimator::update(std::optional<Vector3> accel_body, float dt) noexcept {
    if (!(dt > 0.0F) || !std::isfinite(dt)) return;

    Vector3 phi = delta_theta_ + coning_;
    delta_theta_ = {};
    coning_ = {};
    prev_delta_ = {};
    fast_steps_ = 0;

    if (accel_body && accel_body->finite()) {
        const float magnitude = accel_body->norm();
        const auto a_hat = accel_body->normalized();
        const bool trusted = a_hat && std::fabs(magnitude - kGravity) <= accel_gate_ * kGravity;
        if (trusted) {
            // Куди «низ» дивиться за поточною оцінкою, у осях тіла.
            const Vector3 down_body = q_.rotate_inverse(Vector3{0.0F, 0.0F, 1.0F});
            // Векторний добуток виміряного й очікуваного напрямку — кут неузгодження.
            const Vector3 err = a_hat->cross(down_body);
            phi += err * (gains_.kp * dt);
            // Стала складова неузгодження — це і є зсув нуля гіроскопа.
            bias_ = bias_ - err * (gains_.ki * dt);
        } else {
            // Апарат розганяється: питома сила вже не гравітація, вертикалі з неї не взяти.
            ++rejected_;
        }
    }

    q_ = (q_ * Quaternion::from_rotation_vector(phi)).normalized();
    if (!q_.finite()) {
        q_ = {};
        bias_ = {};
        ++faults_;
    }
}

}  // namespace nav
