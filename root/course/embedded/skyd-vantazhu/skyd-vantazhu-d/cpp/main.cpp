#include <cmath>
#include <expected>
#include <optional>

namespace avionics {

struct Point3D {
    float x{0.0f}; // North (м)
    float y{0.0f}; // East (м)
    float z{0.0f}; // Down (м)
};

struct PayloadCharacteristics {
    float mass_kg{1.5f};
    float drag_coefficient{0.45f};
    float cross_section_area_m2{0.007f};
};

struct AircraftState {
    Point3D position;
    Point3D velocity;
};

struct BallisticPrediction {
    Point3D impact_point;
    float time_of_fall_s{0.0f};
};

enum class BallisticError {
    AlreadyBelowGround,
    MaxStepsExceeded
};

class BallisticIntegrator {
public:
    static constexpr float StandardGravity = 9.80665f;
    static constexpr float StandardDensity = 1.225f;
    static constexpr int MaxSimulationSteps = 300;

    [[nodiscard]] static std::expected<BallisticPrediction, BallisticError>
    predict_impact(const AircraftState& initial,
                   const PayloadCharacteristics& payload,
                   const Point3D& wind_ned,
                   float ground_elevation_down,
                   float time_step_s = 0.05f) noexcept {
        if (initial.position.z >= ground_elevation_down) {
            return std::unexpected(BallisticError::AlreadyBelowGround);
        }

        AircraftState current = initial;
        float elapsed_time = 0.0f;
        const float drag_factor = 0.5f * StandardDensity * payload.drag_coefficient *
                                  payload.cross_section_area_m2 / payload.mass_kg;

        for (int step = 0; step < MaxSimulationSteps; ++step) {
            const AircraftState previous = current;
            const float previous_time = elapsed_time;

            const Point3D relative_velocity{
                current.velocity.x - wind_ned.x,
                current.velocity.y - wind_ned.y,
                current.velocity.z - wind_ned.z
            };

            const float relative_speed = std::sqrt(
                relative_velocity.x * relative_velocity.x +
                relative_velocity.y * relative_velocity.y +
                relative_velocity.z * relative_velocity.z
            );

            const float drag_acceleration = drag_factor * relative_speed;
            const Point3D acceleration{
                -drag_acceleration * relative_velocity.x,
                -drag_acceleration * relative_velocity.y,
                StandardGravity - drag_acceleration * relative_velocity.z
            };

            current.position.x += current.velocity.x * time_step_s + 0.5f * acceleration.x * time_step_s * time_step_s;
            current.position.y += current.velocity.y * time_step_s + 0.5f * acceleration.y * time_step_s * time_step_s;
            current.position.z += current.velocity.z * time_step_s + 0.5f * acceleration.z * time_step_s * time_step_s;

            current.velocity.x += acceleration.x * time_step_s;
            current.velocity.y += acceleration.y * time_step_s;
            current.velocity.z += acceleration.z * time_step_s;

            elapsed_time += time_step_s;

            if (current.position.z >= ground_elevation_down) {
                const float height_delta = current.position.z - previous.position.z;
                const float interpolation = (std::abs(height_delta) > 1e-4f)
                    ? (ground_elevation_down - previous.position.z) / height_delta
                    : 1.0f;

                return BallisticPrediction{
                    Point3D{
                        previous.position.x + interpolation * (current.position.x - previous.position.x),
                        previous.position.y + interpolation * (current.position.y - previous.position.y),
                        ground_elevation_down
                    },
                    previous_time + interpolation * time_step_s
                };
            }
        }

        return std::unexpected(BallisticError::MaxStepsExceeded);
    }
};

} // namespace avionics
