#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <chrono>

// Ідіоматична C++ обгортка над структурою пункту місії
struct MissionWaypoint {
    uint16_t seq{0};
    uint16_t command{16}; // MAV_CMD_NAV_WAYPOINT
    uint8_t frame{6};     // MAV_FRAME_GLOBAL_RELATIVE_ALT_INT
    float hold_time_s{0.0f};
    float acceptance_radius_m{2.0f};
    int32_t latitude_e7{0};
    int32_t longitude_e7{0};
    float relative_altitude_m{10.0f};
    bool autocontinue{true};
};

class FlightPlanBuilder {
public:
    static std::vector<MissionWaypoint> createSamplePlan() {
        return {
            // Точка 0: Точка старту (Home)
            MissionWaypoint{
                .seq = 0,
                .command = 16, // MAV_CMD_NAV_WAYPOINT
                .frame = 5,    // MAV_FRAME_GLOBAL_INT
                .latitude_e7 = static_cast<int32_t>(50.4501 * 1e7),
                .longitude_e7 = static_cast<int32_t>(30.5234 * 1e7),
                .relative_altitude_m = 0.0f
            },
            // Точка 1: Автономний зліт на 15 метрів
            MissionWaypoint{
                .seq = 1,
                .command = 22, // MAV_CMD_NAV_TAKEOFF
                .frame = 6,    // MAV_FRAME_GLOBAL_RELATIVE_ALT_INT
                .latitude_e7 = static_cast<int32_t>(50.4501 * 1e7),
                .longitude_e7 = static_cast<int32_t>(30.5234 * 1e7),
                .relative_altitude_m = 15.0f,
                .autocontinue = true
            },
            // Точка 2: Поворотний вейпоїнт на висоті 25 метрів
            MissionWaypoint{
                .seq = 2,
                .command = 16, // MAV_CMD_NAV_WAYPOINT
                .frame = 6,
                .acceptance_radius_m = 3.0f,
                .latitude_e7 = static_cast<int32_t>(50.4545 * 1e7),
                .longitude_e7 = static_cast<int32_t>(30.5290 * 1e7),
                .relative_altitude_m = 25.0f,
                .autocontinue = true
            }
        };
    }
};
