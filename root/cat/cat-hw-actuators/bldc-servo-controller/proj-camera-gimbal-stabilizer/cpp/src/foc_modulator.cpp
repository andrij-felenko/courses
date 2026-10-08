#include "foc_modulator.hpp"
#include <cmath>
#include <algorithm>

namespace gimbal {

static constexpr float ONE_BY_SQRT3 = 0.5773502691896257f; // 1 / sqrt(3)
static constexpr float SQRT3_BY_TWO = 0.8660254037844386f; // sqrt(3) / 2
static constexpr float TWO_PI = 6.283185307179586f;

float FocModulator::clamp(float val, float min_v, float max_v) {
    return std::max(min_v, std::min(val, max_v));
}

void FocModulator::init(uint8_t pole_pairs, float bus_voltage_v) {
    pole_pairs_ = (pole_pairs > 0) ? pole_pairs : 1;
    bus_voltage_v_ = (bus_voltage_v > 0.0f) ? bus_voltage_v : 12.0f;
    initialized_ = true;
}

float FocModulator::calculate_electrical_angle(float mechanical_angle_rad) const {
    float el_angle = mechanical_angle_rad * static_cast<float>(pole_pairs_);
    // Нормалізація електричного кута в межах [0, 2*PI)
    el_angle = std::fmod(el_angle, TWO_PI);
    if (el_angle < 0.0f) {
        el_angle += TWO_PI;
    }
    return el_angle;
}

AlphaBeta FocModulator::clarke_transform(float ia, float ib, float ic) {
    (void)ic; // При припущенні симетрії ia + ib + ic = 0
    AlphaBeta ab;
    ab.alpha = ia;
    ab.beta = ONE_BY_SQRT3 * (ia + 2.0f * ib);
    return ab;
}

DQ FocModulator::park_transform(AlphaBeta ab, float electrical_angle_rad) {
    float sin_el = std::sin(electrical_angle_rad);
    float cos_el = std::cos(electrical_angle_rad);

    DQ dq;
    dq.d =  ab.alpha * cos_el + ab.beta * sin_el;
    dq.q = -ab.alpha * sin_el + ab.beta * cos_el;
    return dq;
}

AlphaBeta FocModulator::inverse_park_transform(DQ dq, float electrical_angle_rad) {
    float sin_el = std::sin(electrical_angle_rad);
    float cos_el = std::cos(electrical_angle_rad);

    AlphaBeta ab;
    ab.alpha = dq.d * cos_el - dq.q * sin_el;
    ab.beta  = dq.d * sin_el + dq.q * cos_el;
    return ab;
}

DutyCycles FocModulator::compute_svpwm(AlphaBeta ab) {
    // Фазні напруги відносно нейтралі
    float va = ab.alpha;
    float vb = -0.5f * ab.alpha + SQRT3_BY_TWO * ab.beta;
    float vc = -0.5f * ab.alpha - SQRT3_BY_TWO * ab.beta;

    // Введення нульової послідовності (Mid-point voltage injection)
    float v_max = std::max({va, vb, vc});
    float v_min = std::min({va, vb, vc});
    float v_zero = 0.5f * (v_max + v_min);

    // Зміщені фазні напруги для максимального використання DC Bus
    float va_shift = va - v_zero;
    float vb_shift = vb - v_zero;
    float vc_shift = vc - v_zero;

    DutyCycles duty;
    // Перетворення амплітуди напруги в коефіцієнт заповнення ШІМ [0.0, 1.0]
    duty.a = clamp(0.5f + (va_shift / bus_voltage_v_), 0.0f, 1.0f);
    duty.b = clamp(0.5f + (vb_shift / bus_voltage_v_), 0.0f, 1.0f);
    duty.c = clamp(0.5f + (vc_shift / bus_voltage_v_), 0.0f, 1.0f);

    return duty;
}

DutyCycles FocModulator::update(DQ target_dq, float mechanical_angle_rad) {
    float el_angle = calculate_electrical_angle(mechanical_angle_rad);
    AlphaBeta ab = inverse_park_transform(target_dq, el_angle);
    return compute_svpwm(ab);
}

} // namespace gimbal
