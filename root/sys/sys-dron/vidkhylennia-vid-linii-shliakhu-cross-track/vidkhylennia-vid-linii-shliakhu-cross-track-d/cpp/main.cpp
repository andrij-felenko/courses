#include <cmath>
#include <numbers>
#include <algorithm>
#include <optional>

struct Vec2d {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vec2d operator+(const Vec2d& o) const noexcept { return { x + o.x, y + o.y }; }
    [[nodiscard]] constexpr Vec2d operator-(const Vec2d& o) const noexcept { return { x - o.x, y - o.y }; }
    [[nodiscard]] constexpr Vec2d operator*(double s) const noexcept { return { x * s, y * s }; }
    [[nodiscard]] constexpr double dot(const Vec2d& o) const noexcept { return x * o.x + y * o.y; }
    [[nodiscard]] constexpr double cross(const Vec2d& o) const noexcept { return x * o.y - y * o.x; }
    [[nodiscard]] double norm() const noexcept { return std::hypot(x, y); }
};

struct CrossTrackConfig {
    double lookahead_dist{35.0};
    double lookahead_time{2.5};
    double min_lookahead{20.0};
    double max_lookahead{120.0};
    double ki{0.03};
    double int_limit{50.0};
    double max_cross_ang{55.0 * std::numbers::pi / 180.0};
};

struct CrossTrackOutput {
    double ect{0.0};
    double along_track{0.0};
    double progress{0.0};
    Vec2d proj_pt{};
    double course_cmd{0.0};
    double curvature_cmd{0.0};
};

class CrossTrackGuidance {
public:
    explicit CrossTrackGuidance(CrossTrackConfig cfg) : cfg_(cfg) {}

    void reset_integrator() noexcept {
        integrator_state_ = 0.0;
    }

    [[nodiscard]] std::optional<CrossTrackOutput> calculate(Vec2d pos,
                                                           Vec2d wa,
                                                           Vec2d wb,
                                                           double ground_speed,
                                                           double dt) noexcept {
        const Vec2d b = wb - wa;
        const double seg_len = b.norm();

        if (seg_len < 1e-6) {
            return std::nullopt;
        }

        const Vec2d t_hat = b * (1.0 / seg_len);
        const Vec2d a = pos - wa;

        /* 1. Поперечна похибка e_ct = a × t̂ */
        const double ect = a.cross(b) / seg_len;

        /* 2. Поздовжня відстань s = a · t̂ */
        const double s = a.dot(t_hat);
        const double u = s / seg_len;
        const Vec2d proj = wa + t_hat * s;

        /* 3. Адаптивне випередження */
        const double delta_los = std::clamp(std::max(cfg_.lookahead_dist, ground_speed * cfg_.lookahead_time),
                                            cfg_.min_lookahead,
                                            cfg_.max_lookahead);

        /* 4. Інтегратор похибки (ILOS) */
        if (dt > 0.0) {
            integrator_state_ = std::clamp(integrator_state_ + ect * dt,
                                           -cfg_.int_limit,
                                           cfg_.int_limit);
        }
        const double ect_eff = ect + cfg_.ki * integrator_state_;

        /* 5. Розрахунок кутів */
        const double chi_f = std::atan2(b.y, b.x);
        const double chi_cross = std::clamp(std::atan(-ect_eff / delta_los),
                                            -cfg_.max_cross_ang,
                                            cfg_.max_cross_ang);

        const double chi_cmd = wrap_pi(chi_f + chi_cross);
        const double kappa = 2.0 * std::sin(chi_cross) / delta_los;

        return CrossTrackOutput{ ect, s, u, proj, chi_cmd, kappa };
    }

private:
    static double wrap_pi(double rad) noexcept {
        while (rad > std::numbers::pi) rad -= 2.0 * std::numbers::pi;
        while (rad < -std::numbers::pi) rad += 2.0 * std::numbers::pi;
        return rad;
    }

    CrossTrackConfig cfg_;
    double integrator_state_{0.0};
};
