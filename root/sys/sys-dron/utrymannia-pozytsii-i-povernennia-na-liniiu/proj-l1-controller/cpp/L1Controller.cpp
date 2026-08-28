// L1Controller.cpp - Реалізація методів класу L1Controller мовою C++
#include "L1Controller.hpp"

namespace navigation {

std::expected<L1Output, NavigationError> L1Controller::updateLine(
    Vector2D pos,
    Vector2D vel,
    Vector2D wa,
    Vector2D wb,
    float dt) noexcept {
    const float speed = vel.length();
    if (speed < 0.5f) {
        return std::unexpected(NavigationError::ZeroVelocity);
    }

    const Vector2D ab = wb - wa;
    const float ab_len = ab.length();
    if (ab_len < 1.0f) {
        return std::unexpected(NavigationError::DegenerateSegment);
    }

    const Vector2D u_ab = ab * (1.0f / ab_len);
    const Vector2D a = pos - wa;

    const float along_track = a.dot(u_ab);
    const float cross_track = a.cross(u_ab);
    cross_track_error_ = cross_track;

    const float l1 = computeLookaheadDistance(speed);

    // Інтегрування похибки для компенсації вітрового зносу
    if (std::abs(cross_track) < l1) {
        integrator_ect_ += cross_track * params_.k_i * dt;
        integrator_ect_ = std::clamp(integrator_ect_, -params_.i_limit, params_.i_limit);
    }
    const float effective_ct = cross_track + integrator_ect_;

    // Позиція точки прицілювання на лінії
    float along_ref = along_track;
    if (std::abs(effective_ct) < l1) {
        const float dx_ref = std::sqrt(l1 * l1 - effective_ct * effective_ct);
        along_ref += dx_ref;
    } else {
        along_ref += 0.1f * l1;
    }

    const Vector2D p_ref = wa + u_ab * along_ref;
    const Vector2D l1_vec = p_ref - pos;
    const float l1_actual_dist = l1_vec.length();
    if (l1_actual_dist < 0.5f) {
        return std::unexpected(NavigationError::DegenerateSegment);
    }

    // sin(eta) = (V x L1) / (||V|| * ||L1||)
    const float cross_v_l1 = vel.cross(l1_vec) / (speed * l1_actual_dist);
    const float sin_eta = std::clamp(cross_v_l1, -1.0f, 1.0f);

    const float accel = 2.0f * (speed * speed / l1) * sin_eta;
    const float roll = convertAccelToRoll(accel);

    return L1Output{
        .lateral_accel_mps2 = accel,
        .roll_setpoint_rad = roll,
        .cross_track_error_m = cross_track,
        .lookahead_distance_m = l1
    };
}

std::expected<L1Output, NavigationError> L1Controller::updateOrbit(
    Vector2D pos,
    Vector2D vel,
    Vector2D center,
    float radius,
    bool clockwise,
    float dt) noexcept {
    const float speed = vel.length();
    if (speed < 0.5f) {
        return std::unexpected(NavigationError::ZeroVelocity);
    }
    if (radius < 5.0f) {
        return std::unexpected(NavigationError::InvalidRadius);
    }

    const Vector2D d_center = pos - center;
    const float dist_to_center = d_center.length();
    if (dist_to_center < 1.0f) {
        return std::unexpected(NavigationError::InvalidRadius);
    }

    const float sign = clockwise ? 1.0f : -1.0f;
    const float cross_track = sign * (dist_to_center - radius);
    cross_track_error_ = cross_track;

    const float l1 = computeLookaheadDistance(speed);
    const float a_centripetal = sign * (speed * speed / radius);
    const float alpha = std::clamp(l1 / (2.0f * radius), -1.0f, 1.0f);

    const float accel = a_centripetal - 2.0f * (speed * speed / l1) * alpha * (cross_track / l1);
    const float roll = convertAccelToRoll(accel);

    return L1Output{
        .lateral_accel_mps2 = accel,
        .roll_setpoint_rad = roll,
        .cross_track_error_m = cross_track,
        .lookahead_distance_m = l1
    };
}

} // namespace navigation
