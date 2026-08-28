#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <cmath>
#include <cstdint>
#include <string_view>
#include <numbers>

enum class Frame : uint8_t {
    Global = 0,
    LocalNed = 1,
    GlobalRelativeAltInt = 3,
    LocalEnu = 4,
    GlobalTerrainAltInt = 11
};

enum class Command : uint16_t {
    NavWaypoint = 16,
    NavLoiterUnlim = 17,
    NavLoiterTime = 19,
    NavReturnToLaunch = 20,
    NavLand = 21,
    NavTakeoff = 22,
    DoChangeSpeed = 178,
    DoSetServo = 183,
    DoSetCamTriggDist = 206,
    DoJump = 177
};

struct MissionItem {
    float param1{0.0f};
    float param2{0.0f};
    float param3{0.0f};
    float param4{0.0f};
    int32_t x{0};
    int32_t y{0};
    float z{0.0f};
    uint16_t seq{0};
    Command command{Command::NavWaypoint};
    uint8_t target_system{1};
    uint8_t target_component{1};
    Frame frame{Frame::GlobalRelativeAltInt};
    uint8_t current{0};
    uint8_t autocontinue{1};
    uint8_t mission_type{0};

    static constexpr int32_t toDegE7(double deg) noexcept {
        return static_cast<int32_t>(deg * 1.0e7);
    }

    static constexpr double toDeg(int32_t degE7) noexcept {
        return static_cast<double>(degE7) * 1.0e-7;
    }
};

enum class ValidationError {
    EmptyMission,
    SequenceMismatch,
    InvalidCoordinates,
    UnsafeAltitude,
    InvalidJumpTarget
};

constexpr std::string_view errorToString(ValidationError err) noexcept {
    switch (err) {
        case ValidationError::EmptyMission: return "Порожній список елементів місії";
        case ValidationError::SequenceMismatch: return "Порушення монотонної нумерації seq";
        case ValidationError::InvalidCoordinates: return "Географічні координати виходять за діапазон WGS84";
        case ValidationError::UnsafeAltitude: return "Висота точки виходить за безпечні межі польоту";
        case ValidationError::InvalidJumpTarget: return "DO_JUMP посилається на неіснуючий або власний індекс";
    }
    return "Невідома помилка валідації";
}

class MissionPlan {
public:
    void addTakeoff(double lat, double lon, float alt_m) {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::NavTakeoff;
        item.current = item.seq == 0 ? 1 : 0;
        item.x = MissionItem::toDegE7(lat);
        item.y = MissionItem::toDegE7(lon);
        item.z = alt_m;
        items_.push_back(item);
    }

    void addSpeedChange(float speed_m_s) {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::DoChangeSpeed;
        item.param1 = 1.0f; // Groundspeed
        item.param2 = speed_m_s;
        item.param3 = -1.0f;
        items_.push_back(item);
    }

    void addWaypoint(double lat, double lon, float alt_m, float hold_time_s = 0.0f,
                     float accept_radius_m = 5.0f, float pass_radius_m = 0.0f) {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::NavWaypoint;
        item.param1 = hold_time_s;
        item.param2 = accept_radius_m;
        item.param3 = pass_radius_m;
        item.param4 = NAN;
        item.x = MissionItem::toDegE7(lat);
        item.y = MissionItem::toDegE7(lon);
        item.z = alt_m;
        items_.push_back(item);
    }

    void addCameraTriggerDistance(float trigger_dist_m) {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::DoSetCamTriggDist;
        item.param1 = trigger_dist_m;
        item.param3 = 1.0f; // Зробити разовий знімок на початку галса
        items_.push_back(item);
    }

    void addJump(uint16_t target_seq, uint16_t repeat_count) {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::DoJump;
        item.param1 = static_cast<float>(target_seq);
        item.param2 = static_cast<float>(repeat_count);
        items_.push_back(item);
    }

    void addRtl() {
        MissionItem item;
        item.seq = static_cast<uint16_t>(items_.size());
        item.command = Command::NavReturnToLaunch;
        items_.push_back(item);
    }

    [[nodiscard]] std::span<const MissionItem> items() const noexcept {
        return items_;
    }

    [[nodiscard]] std::expected<void, ValidationError> validate() const {
        if (items_.empty()) {
            return std::unexpected(ValidationError::EmptyMission);
        }
        for (size_t i = 0; i < items_.size(); ++i) {
            const auto& it = items_[i];
            if (it.seq != i) {
                return std::unexpected(ValidationError::SequenceMismatch);
            }
            if (it.command == Command::NavWaypoint || it.command == Command::NavTakeoff) {
                double lat = MissionItem::toDeg(it.x);
                double lon = MissionItem::toDeg(it.y);
                if (lat < -90.0 || lat > 90.0 || lon < -180.0 || lon > 180.0) {
                    return std::unexpected(ValidationError::InvalidCoordinates);
                }
                if (it.z < 2.0f || it.z > 5000.0f) {
                    return std::unexpected(ValidationError::UnsafeAltitude);
                }
            }
            if (it.command == Command::DoJump) {
                auto target = static_cast<uint16_t>(it.param1);
                if (target >= items_.size() || target == i) {
                    return std::unexpected(ValidationError::InvalidJumpTarget);
                }
            }
        }
        return {};
    }

    static std::pair<double, double> offsetMeters(double base_lat, double base_lon,
                                                 double d_north_m, double d_east_m) noexcept {
        double lat_rad = base_lat * (std::numbers::pi / 180.0);
        double m_lat = 111132.95;
        double m_lon = 111319.5 * std::cos(lat_rad);
        return {base_lat + (d_north_m / m_lat), base_lon + (d_east_m / m_lon)};
    }

private:
    std::vector<MissionItem> items_;
};

int main() {
    MissionPlan plan;
    double home_lat = 50.4501;
    double home_lon = 30.5234;
    float alt = 60.0f;

    auto [w1_lat, w1_lon] = MissionPlan::offsetMeters(home_lat, home_lon, 100.0, 0.0);
    auto [w2_lat, w2_lon] = MissionPlan::offsetMeters(home_lat, home_lon, 100.0, 300.0);
    auto [w3_lat, w3_lon] = MissionPlan::offsetMeters(home_lat, home_lon, 200.0, 300.0);
    auto [w4_lat, w4_lon] = MissionPlan::offsetMeters(home_lat, home_lon, 200.0, 0.0);

    plan.addTakeoff(home_lat, home_lon, alt);
    plan.addSpeedChange(14.0f);
    plan.addCameraTriggerDistance(20.0f);
    plan.addWaypoint(w1_lat, w1_lon, alt, 0.0f, 5.0f, 12.0f);
    plan.addWaypoint(w2_lat, w2_lon, alt, 0.0f, 5.0f, 12.0f);
    plan.addWaypoint(w3_lat, w3_lon, alt, 0.0f, 5.0f, 12.0f);
    plan.addWaypoint(w4_lat, w4_lon, alt, 0.0f, 5.0f, 12.0f);
    plan.addRtl();

    if (auto res = plan.validate(); res.has_value()) {
        std::cout << "Місія успішно скомпільована та перевірена. Кількість елементів: "
                  << plan.items().size() << '\n';
        for (const auto& it : plan.items()) {
            std::cout << "seq: " << it.seq << ", CMD: " << static_cast<uint16_t>(it.command)
                      << ", X: " << it.x << ", Y: " << it.y << ", Z: " << it.z << " м\n";
        }
    } else {
        std::cerr << "Помилка валідації: " << errorToString(res.error()) << '\n';
    }
    return 0;
}
