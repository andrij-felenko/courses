#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <chrono>
#include <cmath>
#include <optional>
#include <algorithm>

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    constexpr Vec3 operator+(const Vec3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vec3 operator-(const Vec3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vec3 operator*(double s) const noexcept { return {x * s, y * s, z * s}; }
    [[nodiscard]] double dot(const Vec3& o) const noexcept { return x * o.x + y * o.y + z * o.z; }
    [[nodiscard]] double norm() const noexcept { return std::sqrt(dot(*this)); }
};

struct DroneState {
    Vec3 pos;
    Vec3 vel;
    Vec3 acc;
    double yaw{0.0};
};

struct DroneLimits {
    double max_vel{12.0};
    double max_acc{5.0};
    double max_jerk{20.0};
    double safety_dist{0.4};
};

struct SphereObstacle {
    Vec3 center;
    double radius{1.0};
};

/* Одновимірний квінтичний поліном (порядок 6: c0..c5) */
struct Poly1D {
    std::array<double, 6> c{};

    [[nodiscard]] double eval_pos(double t) const noexcept {
        const double t2 = t * t;
        const double t3 = t2 * t;
        const double t4 = t3 * t;
        const double t5 = t4 * t;
        return c[0] + c[1]*t + c[2]*t2 + c[3]*t3 + c[4]*t4 + c[5]*t5;
    }

    [[nodiscard]] double eval_vel(double t) const noexcept {
        const double t2 = t * t;
        const double t3 = t2 * t;
        const double t4 = t3 * t;
        return c[1] + 2.0*c[2]*t + 3.0*c[3]*t2 + 4.0*c[4]*t3 + 5.0*c[5]*t4;
    }

    [[nodiscard]] double eval_acc(double t) const noexcept {
        const double t2 = t * t;
        const double t3 = t2 * t;
        return 2.0*c[2] + 6.0*c[3]*t + 12.0*c[4]*t2 + 20.0*c[5]*t3;
    }
};

struct TrajectorySegment {
    Poly1D px;
    Poly1D py;
    Poly1D pz;
    double duration{1.0};

    [[nodiscard]] Vec3 eval_pos(double t) const noexcept { return {px.eval_pos(t), py.eval_pos(t), pz.eval_pos(t)}; }
    [[nodiscard]] Vec3 eval_vel(double t) const noexcept { return {px.eval_vel(t), py.eval_vel(t), pz.eval_vel(t)}; }
    [[nodiscard]] Vec3 eval_acc(double t) const noexcept { return {px.eval_acc(t), py.eval_acc(t), pz.eval_acc(t)}; }
};

struct Trajectory {
    static constexpr size_t kMaxSegments = 16;
    std::array<TrajectorySegment, kMaxSegments> segments{};
    size_t num_segments{0};
    double total_duration{0.0};
    double cost{0.0};
    uint32_t iteration{0};
    bool is_emergency{false};
    bool is_valid{false};

    [[nodiscard]] std::span<const TrajectorySegment> active_segments() const noexcept {
        return std::span<const TrajectorySegment>(segments.data(), num_segments);
    }
};

class AnytimePlanner {
public:
    explicit AnytimePlanner(DroneLimits limits) noexcept : limits_(limits) {}

    static Poly1D solve_quintic_1d(double p0, double v0, double a0,
                                   double p1, double v1, double a1,
                                   double T) noexcept {
        Poly1D poly;
        poly.c[0] = p0;
        poly.c[1] = v0;
        poly.c[2] = 0.5 * a0;

        const double T2 = T * T;
        const double T3 = T2 * T;
        const double T4 = T3 * T;
        const double T5 = T4 * T;

        const double h = p1 - (p0 + v0 * T + 0.5 * a0 * T2);
        const double v_diff = v1 - (v0 + a0 * T);
        const double a_diff = a1 - a0;

        poly.c[3] = (10.0 * h - 4.0 * v_diff * T + 0.5 * a_diff * T2) / T3;
        poly.c[4] = (-15.0 * h + 7.0 * v_diff * T - a_diff * T2) / T4;
        poly.c[5] = (6.0 * h - 3.0 * v_diff * T + 0.5 * a_diff * T2) / T5;
        return poly;
    }

    [[nodiscard]] bool check_collision(const TrajectorySegment& seg,
                                       std::span<const SphereObstacle> obstacles) const noexcept {
        constexpr int kSamples = 15;
        const double dt = seg.duration / static_cast<double>(kSamples);

        for (int i = 0; i <= kSamples; ++i) {
            const double t = i * dt;
            const Vec3 pos = seg.eval_pos(t);

            for (const auto& obs : obstacles) {
                if ((pos - obs.center).norm() < (obs.radius + limits_.safety_dist)) {
                    return false;
                }
            }
        }
        return true;
    }

    [[nodiscard]] Trajectory generate_emergency_stop(const DroneState& start) const noexcept {
        Trajectory traj;
        traj.num_segments = 1;
        traj.is_emergency = true;

        const double current_speed = start.vel.norm();
        if (current_speed < 0.05) {
            traj.segments[0].duration = 1.0;
            traj.segments[0].px = solve_quintic_1d(start.pos.x, 0, 0, start.pos.x, 0, 0, 1.0);
            traj.segments[0].py = solve_quintic_1d(start.pos.y, 0, 0, start.pos.y, 0, 0, 1.0);
            traj.segments[0].pz = solve_quintic_1d(start.pos.z, 0, 0, start.pos.z, 0, 0, 1.0);
            traj.total_duration = 1.0;
            traj.is_valid = true;
            return traj;
        }

        const double decel = limits_.max_acc * 0.85;
        const double T_brake = std::max(0.2, current_speed / decel);
        const Vec3 stop_pos = start.pos + start.vel * (0.5 * T_brake);

        traj.segments[0].duration = T_brake;
        traj.segments[0].px = solve_quintic_1d(start.pos.x, start.vel.x, start.acc.x, stop_pos.x, 0, 0, T_brake);
        traj.segments[0].py = solve_quintic_1d(start.pos.y, start.vel.y, start.acc.y, stop_pos.y, 0, 0, T_brake);
        traj.segments[0].pz = solve_quintic_1d(start.pos.z, start.vel.z, start.acc.z, stop_pos.z, 0, 0, T_brake);

        traj.total_duration = T_brake;
        traj.cost = 999999.0;
        traj.is_valid = true;
        return traj;
    }

    [[nodiscard]] double compute_cost(const Trajectory& traj) const noexcept {
        double cost = 0.0;
        for (size_t s = 0; s < traj.num_segments; ++s) {
            const auto& seg = traj.segments[s];
            const double T = seg.duration;
            const double c3_sq = seg.px.c[3]*seg.px.c[3] + seg.py.c[3]*seg.py.c[3] + seg.pz.c[3]*seg.pz.c[3];
            const double c4_sq = seg.px.c[4]*seg.px.c[4] + seg.py.c[4]*seg.py.c[4] + seg.pz.c[4]*seg.pz.c[4];
            const double c5_sq = seg.px.c[5]*seg.px.c[5] + seg.py.c[5]*seg.py.c[5] + seg.pz.c[5]*seg.pz.c[5];
            cost += (36.0 * c3_sq * T + 192.0 * c4_sq * T * T * T + 720.0 * c5_sq * std::pow(T, 5));
        }
        return cost;
    }

    [[nodiscard]] Trajectory plan(const DroneState& start_state,
                                  std::span<const Vec3> waypoints,
                                  std::span<const SphereObstacle> obstacles,
                                  std::chrono::microseconds budget) const noexcept {
        using Clock = std::chrono::steady_clock;
        const auto start_time = Clock::now();
        const auto deadline = start_time + budget;

        Trajectory best_traj = generate_emergency_stop(start_state);
        if (waypoints.empty()) {
            return best_traj;
        }

        /* 1. Фаза Seed Trajectory */
        Trajectory seed_traj;
        seed_traj.num_segments = std::min(waypoints.size(), Trajectory::kMaxSegments);
        DroneState curr_wp_state = start_state;
        bool seed_valid = true;
        const double base_T = 1.8;

        for (size_t s = 0; s < seed_traj.num_segments; ++s) {
            const Vec3 target_p = waypoints[s];
            const Vec3 target_v = (s == seed_traj.num_segments - 1) ? Vec3{0, 0, 0} : (target_p - curr_wp_state.pos) * 0.5;
            const Vec3 target_a{0, 0, 0};

            seed_traj.segments[s].duration = base_T;
            seed_traj.segments[s].px = solve_quintic_1d(curr_wp_state.pos.x, curr_wp_state.vel.x, curr_wp_state.acc.x, target_p.x, target_v.x, target_a.x, base_T);
            seed_traj.segments[s].py = solve_quintic_1d(curr_wp_state.pos.y, curr_wp_state.vel.y, curr_wp_state.acc.y, target_p.y, target_v.y, target_a.y, base_T);
            seed_traj.segments[s].pz = solve_quintic_1d(curr_wp_state.pos.z, curr_wp_state.vel.z, curr_wp_state.acc.z, target_p.z, target_v.z, target_a.z, base_T);

            if (!check_collision(seed_traj.segments[s], obstacles)) {
                seed_valid = false;
                break;
            }

            curr_wp_state.pos = target_p;
            curr_wp_state.vel = target_v;
            curr_wp_state.acc = target_a;
        }

        if (seed_valid) {
            seed_traj.total_duration = base_T * static_cast<double>(seed_traj.num_segments);
            seed_traj.cost = compute_cost(seed_traj);
            seed_traj.is_valid = true;
            seed_traj.is_emergency = false;
            seed_traj.iteration = 1;
            best_traj = seed_traj;
        }

        /* 2. Ітеративна оптимізація в межах дедлайну */
        uint32_t iteration = 1;
        while (Clock::now() < deadline) {
            iteration++;
            const double step_scale = std::max(0.4, 1.0 - (0.05 * static_cast<double>(iteration % 10)));

            Trajectory candidate = best_traj;
            candidate.iteration = iteration;
            bool cand_valid = true;
            curr_wp_state = start_state;

            for (size_t s = 0; s < candidate.num_segments; ++s) {
                if (Clock::now() >= deadline) {
                    cand_valid = false;
                    break;
                }

                const Vec3 target_p = waypoints[s];
                const double seg_T = base_T * step_scale;
                candidate.segments[s].duration = seg_T;

                const Vec3 target_v = (s == candidate.num_segments - 1) ? Vec3{0, 0, 0} : (target_p - curr_wp_state.pos) * 0.6;
                const Vec3 target_a{0, 0, 0};

                candidate.segments[s].px = solve_quintic_1d(curr_wp_state.pos.x, curr_wp_state.vel.x, curr_wp_state.acc.x, target_p.x, target_v.x, target_a.x, seg_T);
                candidate.segments[s].py = solve_quintic_1d(curr_wp_state.pos.y, curr_wp_state.vel.y, curr_wp_state.acc.y, target_p.y, target_v.y, target_a.y, seg_T);
                candidate.segments[s].pz = solve_quintic_1d(curr_wp_state.pos.z, curr_wp_state.vel.z, curr_wp_state.acc.z, target_p.z, target_v.z, target_a.z, seg_T);

                if (!check_collision(candidate.segments[s], obstacles)) {
                    cand_valid = false;
                    break;
                }

                curr_wp_state.pos = target_p;
                curr_wp_state.vel = target_v;
                curr_wp_state.acc = target_a;
            }

            if (cand_valid) {
                candidate.cost = compute_cost(candidate);
                if (best_traj.is_emergency || candidate.cost < best_traj.cost) {
                    best_traj = candidate;
                    best_traj.is_emergency = false;
                    best_traj.is_valid = true;
                }
            }
        }

        return best_traj;
    }

private:
    DroneLimits limits_;
};

int main() {
    std::cout << "=== Демонстрація Anytime-планувальника траєкторій (C++) ===\n";

    const DroneState start{
        .pos = {0.0, 0.0, 2.0},
        .vel = {6.0, 1.0, 0.0},
        .acc = {0.0, 0.0, 0.0},
        .yaw = 0.0
    };

    const DroneLimits limits{
        .max_vel = 12.0,
        .max_acc = 5.0,
        .max_jerk = 20.0,
        .safety_dist = 0.4
    };

    const std::array<Vec3, 3> waypoints{{
        {6.0, 2.0, 2.5},
        {12.0, 0.0, 2.0},
        {18.0, 4.0, 3.0}
    }};

    const std::array<SphereObstacle, 2> obstacles{{
        {.center = {6.0, 0.5, 2.2}, .radius = 1.0},
        {.center = {14.0, 2.0, 2.5}, .radius = 0.8}
    }};

    AnytimePlanner planner(limits);

    const auto budget = std::chrono::microseconds(10000); // 10 мс
    const auto t0 = std::chrono::steady_clock::now();
    const Trajectory plan = planner.plan(start, waypoints, obstacles, budget);
    const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - t0);

    std::cout << "Бюджет: " << budget.count() << " мкс | Витрачено: " << elapsed.count() << " мкс\n";
    std::cout << "Статус: " << (plan.is_emergency ? "АВАРІЙНЕ ГАЛЬМУВАННЯ" : "УСПІШНИЙ ПЛАН")
              << " | Ітерацій: " << plan.iteration
              << " | Сегментів: " << plan.num_segments
              << " | Тривалість: " << plan.total_duration << " с"
              << " | Вартість: " << plan.cost << "\n";

    if (plan.is_valid && plan.num_segments > 0) {
        const Vec3 p = plan.segments[0].eval_pos(0.5);
        const Vec3 v = plan.segments[0].eval_vel(0.5);
        std::cout << "Точка t=0.5с: Pos=[" << p.x << ", " << p.y << ", " << p.z
                  << "], Vel=[" << v.x << ", " << v.y << ", " << v.z << "]\n";
    }

    return 0;
}
