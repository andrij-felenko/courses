// ============================================================================
// scurve_planner.hpp
// Сучасний ідіоматичний планувальник 7-сегментної S-кривої на C++20
// ============================================================================
#pragma once
#include <array>
#include <cmath>
#include <concepts>
#include <optional>

struct MotionLimits {
    double max_vel{1.0};   // Максимальна швидкість (од/с)
    double max_acc{1.0};   // Максимальне прискорення (од/с²)
    double max_jerk{1.0};  // Максимальний ривок (од/с³)
};

struct MotionState {
    double pos{0.0};       // Поточне положення s(t)
    double vel{0.0};       // Поточна швидкість v(t)
    double acc{0.0};       // Поточне прискорення a(t)
};

class SCurvePlanner {
public:
    constexpr SCurvePlanner() = default;

    [[nodiscard]] bool plan(double start_pos, double target_pos, const MotionLimits& limits) noexcept {
        if (limits.max_vel <= 0.0 || limits.max_acc <= 0.0 || limits.max_jerk <= 0.0) {
            return false;
        }

        m_start_pos = start_pos;
        m_target_pos = target_pos;
        const double dist = target_pos - start_pos;

        if (std::abs(dist) < 1e-9) {
            m_seg_durations.fill(0.0);
            m_total_time = 0.0;
            m_dir = 1.0;
            m_valid = true;
            return true;
        }

        m_dir = (dist >= 0.0) ? 1.0 : -1.0;
        const double S = std::abs(dist);
        const double v_max = limits.max_vel;
        const double a_max = limits.max_acc;
        const double j_max = limits.max_jerk;

        const double tj = a_max / j_max;
        const double s_limit = 2.0 * (a_max * a_max * a_max) / (j_max * j_max);

        double tj1{0.0}, tj2{0.0}, ta{0.0}, td{0.0}, tv{0.0};

        if (S < s_limit) {
            // Надкороткий рух: прискорення a_max не досягається
            tj1 = std::cbrt(S / (2.0 * j_max));
            tj2 = tj1;
            ta = 0.0;
            td = 0.0;
            tv = 0.0;
        } else {
            const double a_sq_over_j = (a_max * a_max) / j_max;
            const double discr = a_sq_over_j * a_sq_over_j + 4.0 * a_max * S;
            const double v_peak = (-a_sq_over_j + std::sqrt(discr)) * 0.5;

            if (v_peak < v_max) {
                // Трикутний за швидкістю профіль
                tj1 = tj;
                tj2 = tj;
                ta = (v_peak - a_sq_over_j) / a_max;
                td = ta;
                tv = 0.0;
            } else {
                // Повний 7-сегментний рух
                tj1 = tj;
                tj2 = tj;
                ta = (v_max - a_sq_over_j) / a_max;
                td = ta;
                const double s_acc = 0.5 * v_max * (2.0 * tj1 + ta);
                const double s_dec = 0.5 * v_max * (2.0 * tj2 + td);
                tv = std::max(0.0, (S - (s_acc + s_dec)) / v_max);
            }
        }

        m_seg_durations = {tj1, ta, tj1, tv, tj2, td, tj2};
        m_seg_jerks     = {+j_max, 0.0, -j_max, 0.0, -j_max, 0.0, +j_max};

        // Обчислення початкових умов кожного сегмента
        double cur_s{0.0};
        double cur_v{0.0};
        double cur_a{0.0};
        m_total_time = 0.0;

        for (std::size_t i = 0; i < 7; ++i) {
            m_s_start[i] = cur_s;
            m_v_start[i] = cur_v;
            m_a_start[i] = cur_a;
            m_total_time += m_seg_durations[i];

            const double dt = m_seg_durations[i];
            const double j  = m_seg_jerks[i];
            cur_s += cur_v * dt + 0.5 * cur_a * dt * dt + (1.0 / 6.0) * j * dt * dt * dt;
            cur_v += cur_a * dt + 0.5 * j * dt * dt;
            cur_a += j * dt;
        }

        m_valid = true;
        return true;
    }

    [[nodiscard]] MotionState evaluate(double t) const noexcept {
        if (!m_valid) return {};

        if (t <= 0.0) {
            return {m_start_pos, 0.0, 0.0};
        }
        if (t >= m_total_time) {
            return {m_target_pos, 0.0, 0.0};
        }

        double t_accum{0.0};
        std::size_t seg{6};
        for (std::size_t i = 0; i < 7; ++i) {
            if (t < t_accum + m_seg_durations[i]) {
                seg = i;
                break;
            }
            t_accum += m_seg_durations[i];
        }

        const double tau = t - t_accum;
        const double s0 = m_s_start[seg];
        const double v0 = m_v_start[seg];
        const double a0 = m_a_start[seg];
        const double j  = m_seg_jerks[seg];

        const double s_rel = s0 + v0 * tau + 0.5 * a0 * tau * tau + (1.0 / 6.0) * j * tau * tau * tau;
        const double v_rel = v0 + a0 * tau + 0.5 * j * tau * tau;
        const double a_rel = a0 + j * tau;

        return {
            m_start_pos + m_dir * s_rel,
            m_dir * v_rel,
            m_dir * a_rel
        };
    }

    [[nodiscard]] double total_time() const noexcept { return m_total_time; }
    [[nodiscard]] bool is_valid() const noexcept { return m_valid; }

private:
    std::array<double, 7> m_seg_durations{};
    std::array<double, 7> m_seg_jerks{};
    std::array<double, 7> m_s_start{};
    std::array<double, 7> m_v_start{};
    std::array<double, 7> m_a_start{};
    double m_start_pos{0.0};
    double m_target_pos{0.0};
    double m_total_time{0.0};
    double m_dir{1.0};
    bool   m_valid{false};
};
