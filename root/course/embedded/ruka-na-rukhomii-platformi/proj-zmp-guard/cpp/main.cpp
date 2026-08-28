#include <array>
#include <span>
#include <cmath>
#include <algorithm>
#include <numbers>

struct Vector3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct Point2D {
    float x{0.0f};
    float y{0.0f};
};

struct LinkState {
    float mass{0.0f};         // Маса ланки, кг
    Vector3D r{};             // Положення центру мас, м
    Vector3D r_ddot{};        // Лінійне прискорення, м/с^2
    Vector3D H_dot{};         // Швидкість зміни власного кінетичного моменту, Н·м
};

struct ChassisConfig {
    std::span<const Point2D> polygon{};
    float dsm_safe_threshold{0.05f}; // 50 мм запас
    float dsm_critical_limit{0.01f}; // 10 мм критична зона
    float wheel_radius{0.125f};
};

struct StabilityOutput {
    Point2D zmp{};
    float dsm{0.0f};
    float scale_factor{1.0f};
    float feedforward_torque_pitch{0.0f};
    bool is_stable{true};
};

class StabilityGuard {
public:
    static constexpr float GRAVITY = 9.80665f;

    [[nodiscard]] static Point2D compute_zmp(std::span<const LinkState> links) noexcept {
        float sum_denom = 0.0f;
        float sum_num_x = 0.0f;
        float sum_num_y = 0.0f;

        for (const auto& link : links) {
            const float effective_gz = GRAVITY + link.r_ddot.z;
            const float m = link.mass;

            sum_denom += m * effective_gz;
            sum_num_x += m * link.r.x * effective_gz - m * link.r.z * link.r_ddot.x - link.H_dot.y;
            sum_num_y += m * link.r.y * effective_gz - m * link.r.z * link.r_ddot.y + link.H_dot.x;
        }

        if (std::abs(sum_denom) < 1e-4f) {
            return Point2D{0.0f, 0.0f};
        }
        return Point2D{sum_num_x / sum_denom, sum_num_y / sum_denom};
    }

    [[nodiscard]] static float compute_dsm(Point2D pt, std::span<const Point2D> vertices) noexcept {
        if (vertices.size() < 3) return 0.0f;

        float min_dist = 1e6f;
        const std::size_t n = vertices.size();

        for (std::size_t i = 0; i < n; ++i) {
            const auto& v_curr = vertices[i];
            const auto& v_next = vertices[(i + 1) % n];

            const float dx = v_next.x - v_curr.x;
            const float dy = v_next.y - v_curr.y;
            const float len = std::hypot(dx, dy);

            if (len < 1e-5f) continue;

            const float nx = -dy / len;
            const float ny = dx / len;

            const float dist = (pt.x - v_curr.x) * nx + (pt.y - v_curr.y) * ny;
            min_dist = std::min(min_dist, dist);
        }
        return min_dist;
    }

    [[nodiscard]] static StabilityOutput evaluate(
        std::span<const LinkState> links,
        const ChassisConfig& cfg) noexcept 
    {
        StabilityOutput out{};
        out.zmp = compute_zmp(links);
        out.dsm = compute_dsm(out.zmp, cfg.polygon);

        if (out.dsm >= cfg.dsm_safe_threshold) {
            out.scale_factor = 1.0f;
            out.is_stable = true;
        } else if (out.dsm <= cfg.dsm_critical_limit) {
            out.scale_factor = 0.0f;
            out.is_stable = false;
        } else {
            out.scale_factor = (out.dsm - cfg.dsm_critical_limit) / 
                               (cfg.dsm_safe_threshold - cfg.dsm_critical_limit);
            out.is_stable = true;
        }

        float net_reaction_moment_y = 0.0f;
        for (const auto& link : links) {
            net_reaction_moment_y += link.mass * link.r.z * link.r_ddot.x + link.H_dot.y;
        }
        out.feedforward_torque_pitch = -net_reaction_moment_y;

        return out;
    }
};
