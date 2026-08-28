#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <algorithm>
#include <optional>
#include <span>
#include <iomanip>

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    [[nodiscard]] constexpr Vec3 operator*(double s) const noexcept { return {x * s, y * s, z * s}; }

    [[nodiscard]] constexpr double dot(const Vec3& o) const noexcept { return x * o.x + y * o.y + z * o.z; }
    [[nodiscard]] constexpr double norm_sq() const noexcept { return dot(*this); }
    [[nodiscard]] double norm() const noexcept { return std::sqrt(norm_sq()); }

    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }

    [[nodiscard]] Vec3 normalized() const noexcept {
        const double n = norm();
        return (n > 1e-9) ? (*this * (1.0 / n)) : Vec3{};
    }
};

struct KinematicState {
    Vec3 pos{};
    Vec3 vel{};
    Vec3 acc{};
    Vec3 jerk{};
};

struct DroneLimits {
    double max_vel{12.0};      // м/с
    double max_acc{8.0};       // м/с²
    double max_jerk{25.0};     // м/с³
    double safe_radius{0.6};   // м
};

class Poly1D {
public:
    constexpr Poly1D() noexcept = default;

    void solve(double p0, double v0, double a0,
               double p1, double v1, double a1, double T) noexcept {
        const double T2 = T * T;
        const double T3 = T2 * T;
        const double T4 = T3 * T;
        const double T5 = T4 * T;

        c_[0] = p0;
        c_[1] = v0;
        c_[2] = 0.5 * a0;

        const double dp = p1 - (p0 + v0 * T + 0.5 * a0 * T2);
        const double dv = v1 - (v0 + a0 * T);
        const double da = a1 - a0;

        c_[3] = (10.0 * dp - 4.0 * dv * T + 0.5 * da * T2) / T3;
        c_[4] = (-15.0 * dp + 7.0 * dv * T - da * T2) / T4;
        c_[5] = (6.0 * dp - 3.0 * dv * T + 0.5 * da * T2) / T5;
    }

    [[nodiscard]] constexpr double pos(double t) const noexcept {
        return c_[0] + t * (c_[1] + t * (c_[2] + t * (c_[3] + t * (c_[4] + t * c_[5]))));
    }

    [[nodiscard]] constexpr double vel(double t) const noexcept {
        return c_[1] + t * (2.0 * c_[2] + t * (3.0 * c_[3] + t * (4.0 * c_[4] + t * 5.0 * c_[5])));
    }

    [[nodiscard]] constexpr double acc(double t) const noexcept {
        return 2.0 * c_[2] + t * (6.0 * c_[3] + t * (12.0 * c_[4] + t * 20.0 * c_[5]));
    }

    [[nodiscard]] constexpr double jerk(double t) const noexcept {
        return 6.0 * c_[3] + t * (24.0 * c_[4] + t * 60.0 * c_[5]);
    }

private:
    std::array<double, 6> c_{};
};

class Segment3D {
public:
    Segment3D(const KinematicState& start, const KinematicState& end,
              double duration, double start_time = 0.0) noexcept
        : duration_(duration), start_time_(start_time) {
        init(start, end, duration, start_time);
    }

    void init(const KinematicState& start, const KinematicState& end,
              double duration, double start_time) noexcept {
        duration_ = duration;
        start_time_ = start_time;
        px_.solve(start.pos.x, start.vel.x, start.acc.x, end.pos.x, end.vel.x, end.acc.x, duration);
        py_.solve(start.pos.y, start.vel.y, start.acc.y, end.pos.y, end.vel.y, end.acc.y, duration);
        pz_.solve(start.pos.z, start.vel.z, start.acc.z, end.pos.z, end.vel.z, end.acc.z, duration);
    }

    [[nodiscard]] KinematicState evaluate(double global_time) const noexcept {
        const double t = std::clamp(global_time - start_time_, 0.0, duration_);
        return {
            .pos = {px_.pos(t), py_.pos(t), pz_.pos(t)},
            .vel = {px_.vel(t), py_.vel(t), pz_.vel(t)},
            .acc = {px_.acc(t), py_.acc(t), pz_.acc(t)},
            .jerk = {px_.jerk(t), py_.jerk(t), pz_.jerk(t)}
        };
    }

    [[nodiscard]] double duration() const noexcept { return duration_; }
    [[nodiscard]] double start_time() const noexcept { return start_time_; }
    void set_start_time(double t) noexcept { start_time_ = t; }

    bool rescale_if_needed(const DroneLimits& lim, int max_iter = 10) noexcept {
        constexpr int kSamples = 25;
        for (int iter = 0; iter < max_iter; ++iter) {
            double max_v = 0.0;
            double max_a = 0.0;

            for (int i = 0; i <= kSamples; ++i) {
                const double t = start_time_ + (duration_ * i) / kSamples;
                const auto st = evaluate(t);
                max_v = std::max(max_v, st.vel.norm());
                max_a = std::max(max_a, st.acc.norm());
            }

            if (max_v <= lim.max_vel && max_a <= lim.max_acc) {
                return true;
            }

            const double scale_v = max_v / lim.max_vel;
            const double scale_a = std::sqrt(max_a / lim.max_acc);
            const double scale = std::max({scale_v, scale_a, 1.05});

            const auto s0 = evaluate(start_time_);
            const auto s1 = evaluate(start_time_ + duration_);
            init(s0, s1, duration_ * scale, start_time_);
        }
        return false;
    }

private:
    Poly1D px_{}, py_{}, pz_{};
    double duration_{0.0};
    double start_time_{0.0};
};

class Trajectory {
public:
    void clear() noexcept {
        segments_.clear();
        total_duration_ = 0.0;
    }

    void add_segment(const KinematicState& start, const KinematicState& end, double duration) {
        const double start_time = total_duration_;
        segments_.emplace_back(start, end, duration, start_time);
        total_duration_ += duration;
    }

    [[nodiscard]] KinematicState evaluate(double t) const noexcept {
        if (segments_.empty()) return {};
        if (t <= 0.0) return segments_.front().evaluate(0.0);
        if (t >= total_duration_) return segments_.back().evaluate(total_duration_);

        for (const auto& seg : segments_) {
            if (t <= (seg.start_time() + seg.duration())) {
                return seg.evaluate(t);
            }
        }
        return segments_.back().evaluate(total_duration_);
    }

    [[nodiscard]] double total_duration() const noexcept { return total_duration_; }
    [[nodiscard]] std::span<Segment3D> segments() noexcept { return segments_; }
    [[nodiscard]] std::span<const Segment3D> segments() const noexcept { return segments_; }

private:
    std::vector<Segment3D> segments_{};
    double total_duration_{0.0};
};

struct SphereObstacle {
    Vec3 center{};
    double radius{1.0};
};

class KinodynamicReplanner {
public:
    constexpr KinodynamicReplanner(DroneLimits lim, double plan_budget) noexcept
        : limits_(lim), plan_budget_(plan_budget) {}

    [[nodiscard]] std::optional<Trajectory> replan(
        const Trajectory& active_traj,
        double t_now,
        const SphereObstacle& obs,
        const Vec3& goal_pos) const {

        // 1. Прогнозування стану склеювання на момент t_now + t_plan
        const double t_stitch = t_now + plan_budget_;
        const KinematicState s_stitch = active_traj.evaluate(t_stitch);

        // 2. Розрахунок ортогональної обхідної шляхової точки
        Vec3 dir = obs.center - s_stitch.pos;
        const double dist = dir.norm();
        if (dist > 1e-6) dir = dir * (1.0 / dist);
        else dir = Vec3{1.0, 0.0, 0.0};

        const Vec3 up{0.0, 0.0, 1.0};
        Vec3 lateral = dir.cross(up).normalized();
        if (lateral.norm_sq() < 0.01) lateral = Vec3{0.0, 1.0, 0.0};

        const double detour_dist = obs.radius + limits_.safe_radius + 0.8;
        const Vec3 detour_pos = obs.center + lateral * detour_dist;

        KinematicState s_detour{
            .pos = detour_pos,
            .vel = s_stitch.vel * 0.9,
            .acc = Vec3{0.0, 0.0, 0.0},
            .jerk = Vec3{0.0, 0.0, 0.0}
        };

        KinematicState s_goal{
            .pos = goal_pos,
            .vel = Vec3{0.0, 0.0, 0.0},
            .acc = Vec3{0.0, 0.0, 0.0},
            .jerk = Vec3{0.0, 0.0, 0.0}
        };

        // 3. Побудова композитної C²-траєкторії
        Trajectory new_traj;
        const double d1 = (s_detour.pos - s_stitch.pos).norm();
        const double d2 = (s_goal.pos - s_detour.pos).norm();
        const double dur1 = std::max(d1 / (limits_.max_vel * 0.75), 0.5);
        const double dur2 = std::max(d2 / (limits_.max_vel * 0.75), 0.5);

        new_traj.add_segment(s_stitch, s_detour, dur1);
        new_traj.add_segment(s_detour, s_goal, dur2);

        // 4. Верифікація та рескейлінг часу
        for (auto& seg : new_traj.segments()) {
            seg.rescale_if_needed(limits_);
        }
        return new_traj;
    }

private:
    DroneLimits limits_{};
    double plan_budget_{0.030};
};

int main() {
    std::cout << "=== Kinodynamic Replanner Demo (C++20) ===\n";

    const DroneLimits limits{
        .max_vel = 12.0,
        .max_acc = 8.0,
        .max_jerk = 25.0,
        .safe_radius = 0.6
    };

    const KinodynamicReplanner replanner(limits, 0.030);

    Trajectory active_traj;
    const KinematicState s0{.pos = {0.0, 0.0, 2.0}, .vel = {10.0, 0.0, 0.0}};
    const KinematicState s1{.pos = {20.0, 0.0, 2.0}, .vel = {10.0, 0.0, 0.0}};
    active_traj.add_segment(s0, s1, 2.0);

    const SphereObstacle obstacle{.center = {8.0, 0.0, 2.0}, .radius = 1.0};
    constexpr double t_now = 0.200;

    const auto result = replanner.replan(active_traj, t_now, obstacle, s1.pos);
    if (result) {
        std::cout << "Згенеровано нову C²-траєкторію тривалістю " << result->total_duration() << " с\n";
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "  t (s)  |   X (m)   |   Y (m)   |  Vel (m/s) |  Acc (m/s²)\n";
        std::cout << "---------------------------------------------------------\n";
        for (double t = 0.0; t <= result->total_duration(); t += 0.25) {
            const auto st = result->evaluate(t);
            std::cout << std::setw(7) << t << " | "
                      << std::setw(9) << st.pos.x << " | "
                      << std::setw(9) << st.pos.y << " | "
                      << std::setw(10) << st.vel.norm() << " | "
                      << std::setw(11) << st.acc.norm() << "\n";
        }
    }
    return 0;
}
