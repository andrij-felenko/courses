#include <iostream>
#include <vector>
#include <cmath>
#include <optional>
#include <span>
#include <iomanip>
#include <numbers>

namespace flight::trajectory {

struct Vec3 {
    float x{0.0F};
    float y{0.0F};
    float z{0.0F};

    constexpr Vec3 operator+(const Vec3& o) const noexcept { return {x + o.x, y + o.y, z + o.z}; }
    constexpr Vec3 operator-(const Vec3& o) const noexcept { return {x - o.x, y - o.y, z - o.z}; }
    constexpr Vec3 operator*(float s) const noexcept { return {x * s, y * s, z * s}; }
    constexpr Vec3 operator/(float s) const noexcept { return {x / s, y / s, z / s}; }

    [[nodiscard]] constexpr float dot(const Vec3& o) const noexcept { return x * o.x + y * o.y + z * o.z; }
    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return {y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x};
    }
    [[nodiscard]] float norm() const noexcept { return std::sqrt(dot(*this)); }
    [[nodiscard]] Vec3 normalized() const noexcept {
        const float n = norm();
        return (n > 1e-6F) ? (*this / n) : Vec3{};
    }
};

struct Setpoint {
    Vec3 pos;
    Vec3 vel;
    Vec3 acc;
    float jerk_mag{0.0F};
};

struct TrajectoryConfig {
    float max_vel{10.0F};
    float max_acc{4.0F};
    float max_lat_acc{6.0F};
    float max_jerk{20.0F};
    float corner_radius{8.0F};
};

enum class SegmentType { Straight, Arc };

struct TrajectorySegment {
    SegmentType type{SegmentType::Straight};
    float length{0.0F};
    float start_dist{0.0F};
    float v_start{0.0F};
    float v_end{0.0F};
    float duration{0.0F};

    Vec3 p_start;
    Vec3 dir;

    Vec3 arc_center;
    Vec3 n_in;
    Vec3 binormal;
    float radius{0.0F};
    float angle{0.0F};
};

class TrajectoryGenerator {
public:
    explicit TrajectoryGenerator(TrajectoryConfig cfg) noexcept : cfg_{cfg} {}

    bool add_waypoint(const Vec3& wp) {
        if (!waypoints_.empty()) {
            if ((wp - waypoints_.back()).norm() < 1e-2F) {
                return false;
            }
        }
        waypoints_.push_back(wp);
        return true;
    }

    [[nodiscard]] bool plan() {
        if (waypoints_.size() < 2) return false;
        segments_.clear();

        const size_t nw = waypoints_.size();
        std::vector<float> d_lead(nw, 0.0F);
        std::vector<float> r_eff(nw, 0.0F);
        std::vector<float> theta(nw, 0.0F);
        std::vector<Vec3> u_seg(nw - 1);
        std::vector<float> seg_len(nw - 1);

        for (size_t i = 0; i < nw - 1; ++i) {
            const Vec3 diff = waypoints_[i + 1] - waypoints_[i];
            seg_len[i] = diff.norm();
            u_seg[i] = diff / seg_len[i];
        }

        // 1. Геометричний аналіз кутів
        for (size_t i = 1; i < nw - 1; ++i) {
            float cos_t = u_seg[i - 1].dot(u_seg[i]);
            if (cos_t > 0.9999F) continue;
            cos_t = std::clamp(cos_t, -0.9999F, 0.9999F);
            theta[i] = std::acos(cos_t);

            const float half_t = theta[i] * 0.5F;
            const float d_nom = cfg_.corner_radius * std::tan(half_t);
            const float max_d = 0.45F * std::min(seg_len[i - 1], seg_len[i]);
            const float scale = (d_nom > max_d) ? (max_d / d_nom) : 1.0F;

            r_eff[i] = cfg_.corner_radius * scale;
            d_lead[i] = r_eff[i] * std::tan(half_t);
        }

        // 2. Створення сегментів
        float cur_dist = 0.0F;
        for (size_t i = 0; i < nw - 1; ++i) {
            const float start_trim = (i == 0) ? 0.0F : d_lead[i];
            const float end_trim = (i == nw - 2) ? 0.0F : d_lead[i + 1];
            const float straight_len = seg_len[i] - start_trim - end_trim;

            if (straight_len > 1e-5F) {
                TrajectorySegment s{};
                s.type = SegmentType::Straight;
                s.length = straight_len;
                s.start_dist = cur_dist;
                s.dir = u_seg[i];
                s.p_start = waypoints_[i] + u_seg[i] * start_trim;
                cur_dist += straight_len;
                segments_.push_back(s);
            }

            if (i < nw - 2 && theta[i + 1] > 1e-3F) {
                const size_t idx = i + 1;
                TrajectorySegment s{};
                s.type = SegmentType::Arc;
                s.length = r_eff[idx] * theta[idx];
                s.start_dist = cur_dist;
                s.radius = r_eff[idx];
                s.angle = theta[idx];

                const Vec3 t1 = waypoints_[idx] - u_seg[i] * d_lead[idx];
                const Vec3 b = u_seg[i].cross(u_seg[i + 1]).normalized();
                s.binormal = b;
                s.n_in = b.cross(u_seg[i]).normalized();
                s.arc_center = t1 + s.n_in * s.radius;
                s.p_start = t1;

                cur_dist += s->length;
                segments_.push_back(s);
            }
        }
        total_distance_ = cur_dist;

        // 3. Профілювання швидкості
        for (auto& s : segments_) {
            if (s.type == SegmentType::Arc) {
                const float v_corn = std::sqrt(cfg_.max_lat_acc * s.radius);
                s.v_start = std::min(cfg_.max_vel, v_corn);
                s.v_end = s.v_start;
            } else {
                s.v_start = cfg_.max_vel;
                s.v_end = cfg_.max_vel;
            }
        }
        segments_.front().v_start = 0.0F;
        segments_.back().v_end = 0.0F;

        for (int i = static_cast<int>(segments_.size()) - 2; i >= 0; --i) {
            const float max_v = std::sqrt(segments_[i + 1].v_start * segments_[i + 1].v_start +
                                          2.0F * cfg_.max_acc * segments_[i].length);
            segments_[i].v_end = std::min(segments_[i].v_end, segments_[i + 1].v_start);
            segments_[i].v_start = std::min(segments_[i].v_start, max_v);
        }

        float total_t = 0.0F;
        for (auto& s : segments_) {
            const float max_v = std::sqrt(s.v_start * s.v_start + 2.0F * cfg_.max_acc * s.length);
            s.v_end = std::min(s.v_end, max_v);

            float v_avg = 0.5F * (s.v_start + s.v_end);
            if (v_avg < 1e-2F) v_avg = 1e-2F;
            s.duration = s.length / v_avg;
            total_t += s.duration;
        }
        total_duration_ = total_t;
        return true;
    }

    [[nodiscard]] Setpoint sample(float t) const noexcept {
        if (segments_.empty()) return {};
        if (t <= 0.0F) return {segments_.front().p_start, {}, {}};

        float t_acc = 0.0F;
        for (size_t i = 0; i < segments_.size(); ++i) {
            const auto& s = segments_[i];
            if (t <= t_acc + s.duration || i == segments_.size() - 1) {
                const float dt = t - t_acc;
                const float tau = (s.duration > 1e-5F) ? std::clamp(dt / s.duration, 0.0F, 1.0F) : 1.0F;
                const float cur_v = s.v_start + (s.v_end - s.v_start) * tau;
                const float cur_a = (s.duration > 1e-5F) ? (s.v_end - s.v_start) / s.duration : 0.0F;
                const float local_s = s.v_start * dt + 0.5F * cur_a * dt * dt;

                Setpoint sp{};
                if (s.type == SegmentType::Straight) {
                    sp.pos = s.p_start + s.dir * local_s;
                    sp.vel = s.dir * cur_v;
                    sp.acc = s.dir * cur_a;
                } else {
                    const float phi = (s.radius > 1e-5F) ? (local_s / s.radius) : 0.0F;
                    const Vec3 radial = s.n_in * (-std::cos(phi)) + s.binormal.cross(s.n_in) * std::sin(phi);
                    sp.pos = s.arc_center + radial * s.radius;

                    const Vec3 tangent = s.binormal.cross(radial);
                    sp.vel = tangent * cur_v;

                    const Vec3 a_tan = tangent * cur_a;
                    const Vec3 a_rad = radial * (-(cur_v * cur_v) / s.radius);
                    sp.acc = a_tan + a_rad;
                }
                return sp;
            }
            t_acc += s.duration;
        }
        return {waypoints_.back(), {}, {}};
    }

    [[nodiscard]] float total_duration() const noexcept { return total_duration_; }
    [[nodiscard]] float total_distance() const noexcept { return total_distance_; }

private:
    TrajectoryConfig cfg_;
    std::vector<Vec3> waypoints_;
    std::vector<TrajectorySegment> segments_;
    float total_distance_{0.0F};
    float total_duration_{0.0F};
};

} // namespace flight::trajectory

int main() {
    using namespace flight::trajectory;

    TrajectoryConfig cfg{
        .max_vel = 12.0F,
        .max_acc = 4.0F,
        .max_lat_acc = 6.0F,
        .max_jerk = 20.0F,
        .corner_radius = 8.0F
    };

    TrajectoryGenerator generator{cfg};
    generator.add_waypoint({0.0F, 0.0F, 10.0F});
    generator.add_waypoint({50.0F, 0.0F, 10.0F});
    generator.add_waypoint({50.0F, 50.0F, 15.0F});
    generator.add_waypoint({0.0F, 50.0F, 15.0F});

    if (!generator.plan()) {
        std::cerr << "Помилка генерації траєкторії.\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Генератор C++20: Шлях = " << generator.total_distance()
              << " м, Час = " << generator.total_duration() << " с\n";

    for (float t = 0.0F; t <= generator.total_duration() + 0.1F; t += 0.5F) {
        const auto sp = generator.sample(t);
        std::cout << "t = " << std::setw(5) << t
                  << " c | Поз: (" << std::setw(6) << sp.pos.x
                  << ", " << std::setw(6) << sp.pos.y
                  << ", " << std::setw(5) << sp.pos.z << ") м"
                  << " | Швидк: " << std::setw(5) << sp.vel.norm() << " м/с"
                  << " | Приск: " << std::setw(5) << sp.acc.norm() << " м/с²\n";
    }

    return 0;
}
