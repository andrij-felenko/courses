// Приклад використання C++20 класу GeofenceEngine
#include "geofence_engine.hpp"

class FlightNavigationSystem {
public:
    void execute_50hz_step() {
        const auto pos = get_ekf_position();
        const auto vel = get_ekf_velocity();

        const bool is_safe = geofence_.predict_breach(pos, vel);
        if (!is_safe) {
            handle_geofence_breach();
        }
    }

private:
    void handle_geofence_breach() {
        // Перемикання в аварійний режим повернення або гальмування
        failsafe_controller_.trigger_action(drone::geofence::Action::BrakeHold);
    }

    drone::geofence::GeofenceEngine geofence_{
        drone::geofence::GeofenceEngine::Config{
            .max_braking_accel_mps2 = 3.0f,
            .system_latency_s       = 0.25f,
            .static_margin_m        = 4.0f
        }
    };
    FailsafeController failsafe_controller_{};
};
