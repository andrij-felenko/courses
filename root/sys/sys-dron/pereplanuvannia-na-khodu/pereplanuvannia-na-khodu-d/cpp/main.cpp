#include <array>
#include <cmath>
#include <algorithm>
#include <span>

struct TrajectoryPoint {
    double pos{0.0};
    double vel{0.0};
    double acc{0.0};
    double jerk{0.0};
};

class QuinticSegment {
public:
    constexpr QuinticSegment(double p0, double v0, double a0,
                             double p1, double v1, double a1,
                             double duration) noexcept
        : p0_(p0), v0_(v0), a0_(a0), p1_(p1), v1_(v1), a1_(a1), duration_(duration) {
        solve();
    }

    void solve() noexcept {
        const double t1 = duration_;
        const double t2 = t1 * t1;
        const double t3 = t2 * t1;
        const double t4 = t3 * t1;
        const double t5 = t4 * t1;

        c_[0] = p0_;
        c_[1] = v0_;
        c_[2] = 0.5 * a0_;

        const double dp = p1_ - (p0_ + v0_ * t1 + 0.5 * a0_ * t2);
        const double dv = v1_ - (v0_ + a0_ * t1);
        const double da = a1_ - a0_;

        c_[3] = (10.0 * dp - 4.0 * dv * t1 + 0.5 * da * t2) / t3;
        c_[4] = (-15.0 * dp + 7.0 * dv * t1 - da * t2) / t4;
        c_[5] = (6.0 * dp - 3.0 * dv * t1 + 0.5 * da * t2) / t5;
    }

    [[nodiscard]] TrajectoryPoint evaluate(double t) const noexcept {
        const double clamped_t = std::clamp(t, 0.0, duration_);
        const double t2 = clamped_t * clamped_t;
        const double t3 = t2 * clamped_t;
        const double t4 = t3 * clamped_t;
        const double t5 = t4 * clamped_t;

        return {
            .pos = c_[0] + c_[1]*clamped_t + c_[2]*t2 + c_[3]*t3 + c_[4]*t4 + c_[5]*t5,
            .vel = c_[1] + 2.0*c_[2]*clamped_t + 3.0*c_[3]*t2 + 4.0*c_[4]*t3 + 5.0*c_[5]*t4,
            .acc = 2.0*c_[2] + 6.0*c_[3]*clamped_t + 12.0*c_[4]*t2 + 20.0*c_[5]*t3,
            .jerk = 6.0*c_[3] + 24.0*c_[4]*clamped_t + 60.0*c_[5]*t2
        };
    }

    bool scale_duration_if_needed(double v_max, double a_max, int max_iterations = 10) noexcept {
        for (int iter = 0; iter < max_iterations; ++iter) {
            solve();
            double max_v = 0.0;
            double max_a = 0.0;
            constexpr int kSamples = 20;

            for (int i = 0; i <= kSamples; ++i) {
                const double t = (duration_ * i) / kSamples;
                const auto pt = evaluate(t);
                max_v = std::max(max_v, std::abs(pt.vel));
                max_a = std::max(max_a, std::abs(pt.acc));
            }

            if (max_v <= v_max && max_a <= a_max) {
                return true;
            }

            const double scale_v = max_v / v_max;
            const double scale_a = std::sqrt(max_a / a_max);
            const double scale = std::max({scale_v, scale_a, 1.05});
            duration_ *= scale;
        }
        return false;
    }

    [[nodiscard]] double duration() const noexcept { return duration_; }
    [[nodiscard]] std::span<const double, 6> coefficients() const noexcept { return c_; }

private:
    double p0_, v0_, a0_;
    double p1_, v1_, a1_;
    double duration_;
    std::array<double, 6> c_{};
};
