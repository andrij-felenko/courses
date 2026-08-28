#include <cstdint>
#include <chrono>

namespace rf_metrics {

struct GeoPoint3D {
    double x_meters{0.0};
    double y_meters{0.0};
    double z_meters{0.0};
};

struct SensorNode {
    std::uint32_t station_id{0};
    GeoPoint3D location;
    std::chrono::nanoseconds timestamp{0};
    double snr_db{0.0};
    bool sync_locked{false};
};

struct LocalizationResult {
    GeoPoint3D estimated_pos;
    double gdop{0.0};
    double confidence_radius_m{0.0};
    std::uint32_t iterations_used{0};
    bool converged{false};
};

} // namespace rf_metrics
