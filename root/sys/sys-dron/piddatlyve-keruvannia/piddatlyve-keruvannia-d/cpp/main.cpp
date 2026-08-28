#include <array>
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <span>

namespace drone::control {

inline constexpr std::size_t kCartesianDof = 6;
using Vector6d = std::array<double, kCartesianDof>;

struct AdmittanceConfig {
    Vector6d virtual_mass{1.5, 1.5, 1.5, 0.08, 0.08, 0.08};       // кг, кг·м²
    Vector6d virtual_damping{60.0, 60.0, 60.0, 2.5, 2.5, 2.5};    // Н·с/м, Н·м·с/рад
    Vector6d virtual_stiffness{400.0, 400.0, 400.0, 15.0, 15.0, 15.0}; // Н/м, Н·м/рад
    Vector6d sensor_deadband{1.5, 1.5, 1.5, 0.08, 0.08, 0.08};     // Поріг шуму давача
    Vector6d max_velocity{0.4, 0.4, 0.4, 1.2, 1.2, 1.2};          // м/с, рад/с
    Vector6d max_displacement{0.15, 0.15, 0.15, 0.6, 0.6, 0.6};   // м, рад
};

class SpatialAdmittanceController {
public:
    explicit SpatialAdmittanceController(AdmittanceConfig config) noexcept
        : config_(config), displacement_{}, velocity_{}, acceleration_{} {}

    void reset() noexcept {
        displacement_.fill(0.0);
        velocity_.fill(0.0);
        acceleration_.fill(0.0);
    }

    [[nodiscard]] Vector6d update(std::span<const double, kCartesianDof> wrench_measured,
                                  std::span<const double, kCartesianDof> wrench_desired,
                                  std::span<const double, kCartesianDof> pose_nominal,
                                  double dt) noexcept {
        Vector6d pose_command{};
        if (dt <= 0.0) {
            std::ranges::copy(pose_nominal, pose_command.begin());
            return pose_command;
        }

        for (std::size_t i = 0; i < kCartesianDof; ++i) {
            // 1. Нелінійна фільтрація мертвої зони для придушення високочастотного шуму
            const double raw_err = wrench_measured[i] - wrench_desired[i];
            const double threshold = config_.sensor_deadband[i];
            double filtered_force_error = 0.0;

            if (std::abs(raw_err) > threshold) {
                filtered_force_error = (raw_err > 0.0) ? (raw_err - threshold) : (raw_err + threshold);
            }

            // 2. Цільове прискорення адмітансу: acc = M_d⁻¹ · (F_err - B_d·vel - K_d·pos)
            const double mass = std::max(config_.virtual_mass[i], 1e-3);
            const double net_force = filtered_force_error 
                                   - (config_.virtual_damping[i] * velocity_[i]) 
                                   - (config_.virtual_stiffness[i] * displacement_[i]);
            acceleration_[i] = net_force / mass;

            // 3. Симплектичний напівнеявний інтегратор Ейлера (Euler-Cromer)
            velocity_[i] += acceleration_[i] * dt;
            velocity_[i] = std::clamp(velocity_[i], -config_.max_velocity[i], config_.max_velocity[i]);

            displacement_[i] += velocity_[i] * dt;
            
            // Обмеження робочої зони деформації
            if (std::abs(displacement_[i]) > config_.max_displacement[i]) {
                displacement_[i] = std::clamp(displacement_[i], 
                                              -config_.max_displacement[i], 
                                              config_.max_displacement[i]);
                velocity_[i] = 0.0;
            }

            // 4. Коригування просторової траєкторії для сервоприводів
            pose_command[i] = pose_nominal[i] - displacement_[i];
        }

        return pose_command;
    }

    [[nodiscard]] const Vector6d& displacement() const noexcept { return displacement_; }
    [[nodiscard]] const Vector6d& velocity() const noexcept { return velocity_; }

private:
    AdmittanceConfig config_;
    Vector6d displacement_;
    Vector6d velocity_;
    Vector6d acceleration_;
};

} // namespace drone::control
