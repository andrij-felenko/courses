#include <cmath>
#include <numbers>

namespace kinematics {

struct ChassisGeometry {
    double wheelbase{2.5}; // Повна колісна база L, м
    double rear_to_cg{1.2}; // Відстань від задньої осі до центру мас, м
};

struct Pose2D {
    double x{0.0};
    double y{0.0};
    double theta{0.0};
};

class KinematicIntegrator {
public:
    explicit constexpr KinematicIntegrator(ChassisGeometry geom) noexcept
        : geom_{geom} {}

    void step(Pose2D& pose, double v, double delta, double dt) const noexcept {
        const double beta = std::atan((geom_.rear_to_cg / geom_.wheelbase) * std::tan(delta));
        const double omega = (v / geom_.wheelbase) * std::tan(delta) * std::cos(beta);
        const double dtheta = omega * dt;

        if (std::abs(omega) > 1e-5) {
            const double R = v / omega;
            const double heading_start = pose.theta + beta;
            const double heading_end = heading_start + dtheta;

            pose.x += R * (std::sin(heading_end) - std::sin(heading_start));
            pose.y += R * (std::cos(heading_start) - std::cos(heading_end));
        } else {
            const double heading = pose.theta + beta;
            pose.x += v * std::cos(heading) * dt;
            pose.y += v * std::sin(heading) * dt;
        }

        pose.theta = normalize_angle(pose.theta + dtheta);
    }

private:
    ChassisGeometry geom_;

    [[nodiscard]] static double normalize_angle(double angle) noexcept {
        while (angle > std::numbers::pi)  angle -= 2.0 * std::numbers::pi;
        while (angle < -std::numbers::pi) angle += 2.0 * std::numbers::pi;
        return angle;
    }
};

} // namespace kinematics
