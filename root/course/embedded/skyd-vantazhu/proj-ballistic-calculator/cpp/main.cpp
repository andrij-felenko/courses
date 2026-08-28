#include <array>
#include <cmath>
#include <expected>
#include <numbers>

namespace avionics::ballistics {

inline constexpr float Gravity = 9.80665f;
inline constexpr float AirDensity = 1.225f;
inline constexpr std::size_t MaxBallisticSteps = 300;

enum class CalculationError {
    BelowTargetElevation,
    StepLimitExceeded,
    InvalidMass
};

struct Vector3D {
    float x{0.0f}; // North (м)
    float y{0.0f}; // East (м)
    float z{0.0f}; // Down (м, додатне вниз)

    constexpr Vector3D operator+(const Vector3D& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    constexpr Vector3D operator-(const Vector3D& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
    constexpr Vector3D operator*(float scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
    [[nodiscard]] float norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
    [[nodiscard]] float horizontal_norm() const noexcept {
        return std::sqrt(x * x + y * y);
    }
};

struct PayloadProfile {
    float mass_kg{1.5f};
    float drag_coefficient{0.45f};
    float cross_section_area_m2{0.007f};
};

struct KinematicState {
    Vector3D position;
    Vector3D velocity;
};

struct Environment {
    Vector3D wind_velocity; // Вітер (North, East, Down)
    float target_elevation_down{0.0f};
    float actuator_latency_s{0.10f};
};

struct CcrpSolution {
    Vector3D impact_point;
    Vector3D release_offset;
    float time_of_fall_s{0.0f};
    float time_to_release_s{0.0f};
    float distance_to_release_m{0.0f};
    bool is_in_release_gate{false};
};

class BallisticCalculator {
public:
    [[nodiscard]] static std::expected<std::pair<Vector3D, float>, CalculationError>
    integrate_trajectory(const KinematicState& initial,
                         const PayloadProfile& payload,
                         const Environment& env,
                         float dt = 0.05f) noexcept {
        if (initial.position.z >= env.target_elevation_down) {
            return std::unexpected(CalculationError::BelowTargetElevation);
        }

        KinematicState state = initial;
        float time_elapsed = 0.0f;

        const float k_drag = 0.5f * AirDensity * payload.drag_coefficient *
                             payload.cross_section_area_m2 / payload.mass_kg;

        auto compute_deriv = [&](const KinematicState& s) noexcept -> KinematicState {
            const Vector3D v_rel = s.velocity - env.wind_velocity;
            const float speed_rel = v_rel.norm();
            const float factor = k_drag * speed_rel;
            return {
                s.velocity,
                {
                    -factor * v_rel.x,
                    -factor * v_rel.y,
                    Gravity - factor * v_rel.z
                }
            };
        };

        for (std::size_t step = 0; step < MaxBallisticSteps; ++step) {
            const KinematicState prev_state = state;
            const float prev_t = time_elapsed;

            // RK4 інтегрування
            const auto k1 = compute_deriv(state);
            const auto k2 = compute_deriv({state.position + k1.position * (dt * 0.5f),
                                           state.velocity + k1.velocity * (dt * 0.5f)});
            const auto k3 = compute_deriv({state.position + k2.position * (dt * 0.5f),
                                           state.velocity + k2.velocity * (dt * 0.5f)});
            const auto k4 = compute_deriv({state.position + k3.position * dt,
                                           state.velocity + k3.velocity * dt});

            state.position = state.position +
                (k1.position + k2.position * 2.0f + k3.position * 2.0f + k4.position) * (dt / 6.0f);
            state.velocity = state.velocity +
                (k1.velocity + k2.velocity * 2.0f + k3.velocity * 2.0f + k4.velocity) * (dt / 6.0f);

            time_elapsed += dt;

            // Перетин площини рельєфу цілі
            if (state.position.z >= env.target_elevation_down) {
                const float dz = state.position.z - prev_state.position.z;
                const float ratio = (std::abs(dz) > 1e-4f)
                    ? (env.target_elevation_down - prev_state.position.z) / dz
                    : 1.0f;

                const Vector3D impact{
                    prev_state.position.x + ratio * (state.position.x - prev_state.position.x),
                    prev_state.position.y + ratio * (state.position.y - prev_state.position.y),
                    env.target_elevation_down
                };
                return std::make_pair(impact, prev_t + ratio * dt);
            }
        }

        return std::unexpected(CalculationError::StepLimitExceeded);
    }

    [[nodiscard]] static std::expected<CcrpSolution, CalculationError>
    compute_ccrp(const KinematicState& uav,
                 const Vector3D& target_ground,
                 const PayloadProfile& payload,
                 const Environment& env,
                 float gate_radius_m = 4.0f) noexcept {
        auto trajectory_res = integrate_trajectory(uav, payload, env);
        if (!trajectory_res) {
            return std::unexpected(trajectory_res.error());
        }

        const auto& [impact, tof] = *trajectory_res;
        CcrpSolution solution;
        solution.impact_point = impact;
        solution.time_of_fall_s = tof;
        solution.release_offset = impact - uav.position;

        // Врахування апаратного запізнення
        const Vector3D actuator_lead = uav.velocity * env.actuator_latency_s;
        const Vector3D total_lead = solution.release_offset + actuator_lead;

        const Vector3D ideal_release{
            target_ground.x - total_lead.x,
            target_ground.y - total_lead.y,
            uav.position.z
        };

        const Vector3D to_release = ideal_release - uav.position;
        solution.distance_to_release_m = to_release.horizontal_norm();

        const float ground_speed = uav.velocity.horizontal_norm();
        if (ground_speed > 0.5f) {
            const float dot = (to_release.x * uav.velocity.x + to_release.y * uav.velocity.y) / ground_speed;
            solution.time_to_release_s = dot / ground_speed;
        } else {
            solution.time_to_release_s = 999.0f;
        }

        solution.is_in_release_gate = (solution.distance_to_release_m <= gate_radius_m) &&
                                      (solution.time_to_release_s >= -0.1f && solution.time_to_release_s <= 0.15f);

        return solution;
    }

    // Компенсація стрибка тяги при скиданні 30–50% маси
    [[nodiscard]] static constexpr float
    compensate_throttle(float current_hover_throttle,
                        float total_mass_kg,
                        float dropped_mass_kg) noexcept {
        if (total_mass_kg <= dropped_mass_kg || total_mass_kg <= 0.1f) {
            return current_hover_throttle;
        }
        return current_hover_throttle * ((total_mass_kg - dropped_mass_kg) / total_mass_kg);
    }
};

} // namespace avionics::ballistics
