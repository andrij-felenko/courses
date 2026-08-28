#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <span>
#include <iomanip>
#include <optional>

struct Vec2 {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vec2 operator+(const Vec2& o) const noexcept { return { x + o.x, y + o.y }; }
    [[nodiscard]] constexpr Vec2 operator-(const Vec2& o) const noexcept { return { x - o.x, y - o.y }; }
    [[nodiscard]] constexpr Vec2 operator*(double s) const noexcept { return { x * s, y * s }; }
    [[nodiscard]] constexpr double dot(const Vec2& o) const noexcept { return x * o.x + y * o.y; }
    [[nodiscard]] constexpr double cross(const Vec2& o) const noexcept { return x * o.y - y * o.x; }
    [[nodiscard]] double norm() const noexcept { return std::hypot(x, y); }
};

struct Waypoint {
    Vec2 pos;
    double acceptance_radius{20.0};
};

struct LosConfig {
    double lookahead_distance{35.0}; /* Базове випередження Delta_los [м] */
    double lookahead_time{2.5};      /* Часовий коефіцієнт k_t [с] */
    double min_lookahead{20.0};      /* Нижня межа Delta [м] */
    double max_lookahead{120.0};     /* Верхня межа Delta [м] */
    double ki_cross_track{0.03};     /* Коефіцієнт інтегратора вітру [1/с] */
    double integrator_max{50.0};     /* Поріг анти-вінд-ап [м*с] */
    double max_approach_angle{55.0 * std::numbers::pi / 180.0}; /* Граничний кут захоплення [рад] */
};

struct GuidanceState {
    double cross_track_error{0.0};   /* e_ct [м] */
    double along_track_dist{0.0};    /* s [м] */
    double normalized_progress{0.0}; /* u in [0, 1] */
    Vec2 projection_point{};         /* p_proj [м] */
    double segment_length{0.0};      /* L_AB [м] */
    double segment_course{0.0};      /* chi_F [рад] */
    double command_course{0.0};      /* chi_cmd [рад] */
    double curvature_cmd{0.0};       /* kappa [1/м] */
    std::size_t current_segment_idx{0};
    bool mission_completed{false};
};

class PathTrackingController {
public:
    PathTrackingController(std::span<const Waypoint> waypoints, LosConfig config)
        : waypoints_(waypoints), config_(config) {
        state_.mission_completed = (waypoints_.size() < 2);
    }

    void update(Vec2 current_pos, double ground_speed, double dt) {
        if (state_.mission_completed || waypoints_.size() < 2) {
            return;
        }

        auto idx = state_.current_segment_idx;
        const auto& wa = waypoints_[idx].pos;
        const auto& wb = waypoints_[idx + 1].pos;
        const auto r_acc = waypoints_[idx + 1].acceptance_radius;

        const auto geom = calculate_geometry(current_pos, wa, wb);
        if (!geom) {
            advance_segment();
            return;
        }

        auto [ect, s, u, proj, len, chi_f] = *geom;

        /* Перевірка досягнення цільової точки: радіус або перетин площини */
        const auto dist_to_wb = (current_pos - wb).norm();
        if (dist_to_wb <= r_acc || s >= len) {
            if (idx + 2 < waypoints_.size()) {
                state_.current_segment_idx++;
                idx = state_.current_segment_idx;
                const auto next_geom = calculate_geometry(current_pos, waypoints_[idx].pos, waypoints_[idx + 1].pos);
                if (next_geom) {
                    std::tie(ect, s, u, proj, len, chi_f) = *next_geom;
                }
            } else {
                state_.mission_completed = true;
            }
        }

        /* Адаптивна дистанція прямої видимості */
        double delta_los = std::clamp(std::max(config_.lookahead_distance, ground_speed * config_.lookahead_time),
                                      config_.min_lookahead,
                                      config_.max_lookahead);

        /* Інтегратор бокового відхилення (ILOS) */
        cross_track_integral_ = std::clamp(cross_track_integral_ + ect * dt,
                                           -config_.integrator_max,
                                           config_.integrator_max);

        const double ect_effective = ect + config_.ki_cross_track * cross_track_integral_;

        /* Розрахунок кута корекції та бажаного курсу */
        const double chi_cross = std::clamp(std::atan(-ect_effective / delta_los),
                                            -config_.max_approach_angle,
                                            config_.max_approach_angle);

        state_.cross_track_error = ect;
        state_.along_track_dist = s;
        state_.normalized_progress = u;
        state_.projection_point = proj;
        state_.segment_length = len;
        state_.segment_course = chi_f;
        state_.command_course = wrap_angle(chi_f + chi_cross);
        state_.curvature_cmd = 2.0 * std::sin(chi_cross) / delta_los;
    }

    [[nodiscard]] const GuidanceState& state() const noexcept { return state_; }

private:
    struct GeometryResult {
        double ect;
        double s;
        double u;
        Vec2 proj;
        double len;
        double chi_f;
    };

    static std::optional<GeometryResult> calculate_geometry(Vec2 pos, Vec2 wa, Vec2 wb) {
        const Vec2 b = wb - wa;
        const double len = b.norm();
        if (len < 1e-6) {
            return std::nullopt;
        }

        const Vec2 a = pos - wa;
        const Vec2 t_hat = b * (1.0 / len);

        const double ect = a.cross(b) / len;
        const double s = a.dot(t_hat);
        const double u = s / len;
        const Vec2 proj = wa + t_hat * s;
        const double chi_f = std::atan2(b.y, b.x);

        return GeometryResult{ ect, s, u, proj, len, chi_f };
    }

    void advance_segment() {
        state_.current_segment_idx++;
        if (state_.current_segment_idx >= waypoints_.size() - 1) {
            state_.mission_completed = true;
        }
    }

    static double wrap_angle(double rad) noexcept {
        while (rad > std::numbers::pi) rad -= 2.0 * std::numbers::pi;
        while (rad < -std::numbers::pi) rad += 2.0 * std::numbers::pi;
        return rad;
    }

    std::span<const Waypoint> waypoints_;
    LosConfig config_;
    GuidanceState state_{};
    double cross_track_integral_{0.0};
};

int main() {
    const std::vector<Waypoint> mission = {
        { .pos = { 0.0, 0.0 },       .acceptance_radius = 15.0 },
        { .pos = { 500.0, 0.0 },     .acceptance_radius = 20.0 },
        { .pos = { 500.0, 400.0 },   .acceptance_radius = 20.0 },
        { .pos = { 1000.0, 400.0 },  .acceptance_radius = 20.0 }
    };

    LosConfig config{
        .lookahead_distance = 35.0,
        .lookahead_time = 2.5,
        .min_lookahead = 20.0,
        .max_lookahead = 120.0,
        .ki_cross_track = 0.03,
        .integrator_max = 50.0,
        .max_approach_angle = 55.0 * std::numbers::pi / 180.0
    };

    PathTrackingController controller(mission, config);

    Vec2 pos{ 10.0, 25.0 };
    double speed = 16.0;
    double course = 0.0;
    constexpr double dt = 0.1;

    std::cout << std::fixed << std::setprecision(1);
    std::cout << "=== Симуляція ведення по місії (C++20 ILOS) ===\n";
    std::cout << "Час [с] | X [м]    | Y [м]   | e_ct [м] | s [м]   | Курс [°] | Ціль [°] | Сегмент\n";
    std::cout << "-----------------------------------------------------------------------------\n";

    for (int step = 0; step <= 350; ++step) {
        const double sim_time = step * dt;

        controller.update(pos, speed, dt);
        const auto& st = controller.state();

        if (step % 25 == 0) {
            std::cout << std::setw(7) << sim_time << " | "
                      << std::setw(7) << pos.x << " | "
                      << std::setw(7) << pos.y << " | "
                      << std::setw(8) << std::setprecision(2) << st.cross_track_error << " | "
                      << std::setw(7) << std::setprecision(1) << st.along_track_dist << " | "
                      << std::setw(8) << course * (180.0 / std::numbers::pi) << " | "
                      << std::setw(8) << st.command_course * (180.0 / std::numbers::pi) << " | "
                      << st.current_segment_idx << " -> " << st.current_segment_idx + 1 << "\n";
        }

        if (st.mission_completed) {
            std::cout << "Маршрут успішно завершено у часі " << sim_time << " с.\n";
            break;
        }

        const double course_err = PathTrackingController::wrap_angle(st.command_course - course);
        course += (course_err / 0.6) * dt;
        course = PathTrackingController::wrap_angle(course);

        pos.x += speed * std::cos(course) * dt;
        pos.y += speed * std::sin(course) * dt;
    }

    return 0;
}
