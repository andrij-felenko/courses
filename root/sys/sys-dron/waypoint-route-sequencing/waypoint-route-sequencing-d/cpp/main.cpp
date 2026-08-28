#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>
#include <vector>

namespace navigation {

constexpr float EarthRadiusMeters = 6371000.0f;

enum class YawMode : uint8_t {
    AlongTrack = 0,
    Fixed      = 1,
    Roi        = 2
};

enum class SequencerState : uint8_t {
    Idle,
    Navigating,
    LoiterHold,
    ExecuteAction,
    AdvanceWaypoint,
    MissionDone
};

struct Waypoint {
    double latitudeDeg;
    double longitudeDeg;
    float altitudeM;
    float cruiseSpeedMs{5.0f};
    float acceptanceRadiusM{2.0f};
    float holdTimeSec{0.0f};
    float yawTargetRad{0.0f};
    YawMode yawMode{YawMode::AlongTrack};
    uint16_t actionId{0};
    bool flyThrough{true};
};

struct Vector3D {
    float x{0.0f}; // North (м)
    float y{0.0f}; // East (м)
    float z{0.0f}; // Down (м)

    [[nodiscard]] constexpr float dot(const Vector3D& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }

    [[nodiscard]] float length() const noexcept {
        return std::sqrt(dot(*this));
    }

    [[nodiscard]] float distance2D(const Vector3D& other) const noexcept {
        const float dx = x - other.x;
        const float dy = y - other.y;
        return std::sqrt(dx * dx + dy * dy);
    }

    [[nodiscard]] Vector3D normalized() const noexcept {
        const float len = length();
        return len > 0.001f ? Vector3D{x / len, y / len, z / len} : Vector3D{1.0f, 0.0f, 0.0f};
    }
};

struct VehicleState {
    Vector3D position;
    Vector3D velocity;
    float yawRad{0.0f};
};

struct NavigationSetpoint {
    Vector3D targetPosition;
    Vector3D targetVelocity;
    float targetYawRad{0.0f};
    bool triggerAction{false};
};

class MissionSequencer {
public:
    MissionSequencer(std::span<const Waypoint> missionPlan,
                     double homeLatDeg, double homeLonDeg, float homeAltM)
        : m_plan(missionPlan),
          m_homeLat(homeLatDeg),
          m_homeLon(homeLonDeg),
          m_homeAlt(homeAltM),
          m_state(missionPlan.empty() ? SequencerState::Idle : SequencerState::Navigating) {
        if (!m_plan.empty()) {
            m_prevWpNed = geoToNed(m_homeLat, m_homeLon, m_homeAlt);
            m_currWpNed = geoToNed(m_plan[0].latitudeDeg, m_plan[0].longitudeDeg, m_plan[0].altitudeM);
            m_segmentUnitIn = (m_currWpNed.distance2D(m_prevWpNed) > 0.001f)
                                  ? Vector3D{m_currWpNed.x - m_prevWpNed.x,
                                             m_currWpNed.y - m_prevWpNed.y,
                                             m_currWpNed.z - m_prevWpNed.z}.normalized()
                                  : Vector3D{1.0f, 0.0f, 0.0f};
        }
    }

    void setRegionOfInterest(double latDeg, double lonDeg, float altM) noexcept {
        m_roiNed = geoToNed(latDeg, lonDeg, altM);
    }

    void clearRegionOfInterest() noexcept {
        m_roiNed.reset();
    }

    [[nodiscard]] SequencerState currentState() const noexcept { return m_state; }
    [[nodiscard]] size_t currentWaypointIndex() const noexcept { return m_currentIndex; }

    NavigationSetpoint update(const VehicleState& vehicle, float dtSec) {
        NavigationSetpoint setpoint{};
        setpoint.targetPosition = m_currWpNed;

        if (m_state == SequencerState::Idle || m_state == SequencerState::MissionDone) {
            setpoint.targetVelocity = Vector3D{0.0f, 0.0f, 0.0f};
            setpoint.targetYawRad = vehicle.yawRad;
            return setpoint;
        }

        const auto& currentWp = m_plan[m_currentIndex];

        switch (m_state) {
        case SequencerState::Navigating: {
            if (isWaypointReached(vehicle, currentWp)) {
                if (currentWp.flyThrough && currentWp.holdTimeSec <= 0.001f) {
                    m_state = SequencerState::AdvanceWaypoint;
                } else {
                    m_state = SequencerState::LoiterHold;
                    m_holdTimer = currentWp.holdTimeSec;
                }
            } else {
                const Vector3D toTarget{
                    m_currWpNed.x - vehicle.position.x,
                    m_currWpNed.y - vehicle.position.y,
                    m_currWpNed.z - vehicle.position.z
                };
                const float dist = toTarget.length();
                if (dist > 0.001f) {
                    const float speed = currentWp.cruiseSpeedMs;
                    setpoint.targetVelocity = Vector3D{
                        (toTarget.x / dist) * speed,
                        (toTarget.y / dist) * speed,
                        (toTarget.z / dist) * speed
                    };
                }
            }
            break;
        }

        case SequencerState::LoiterHold: {
            setpoint.targetVelocity = Vector3D{0.0f, 0.0f, 0.0f};
            m_holdTimer -= dtSec;
            if (m_holdTimer <= 0.0f) {
                m_state = (currentWp.actionId != 0) ? SequencerState::ExecuteAction
                                                    : SequencerState::AdvanceWaypoint;
            }
            break;
        }

        case SequencerState::ExecuteAction: {
            setpoint.targetVelocity = Vector3D{0.0f, 0.0f, 0.0f};
            setpoint.triggerAction = true;
            m_state = SequencerState::AdvanceWaypoint;
            break;
        }

        case SequencerState::AdvanceWaypoint: {
            m_currentIndex++;
            if (m_currentIndex >= m_plan.size()) {
                m_state = SequencerState::MissionDone;
                setpoint.targetVelocity = Vector3D{0.0f, 0.0f, 0.0f};
            } else {
                m_prevWpNed = m_currWpNed;
                const auto& nextWp = m_plan[m_currentIndex];
                m_currWpNed = geoToNed(nextWp.latitudeDeg, nextWp.longitudeDeg, nextWp.altitudeM);

                const Vector3D seg{
                    m_currWpNed.x - m_prevWpNed.x,
                    m_currWpNed.y - m_prevWpNed.y,
                    m_currWpNed.z - m_prevWpNed.z
                };
                m_segmentUnitIn = seg.normalized();
                m_state = SequencerState::Navigating;
            }
            break;
        }

        default:
            break;
        }

        setpoint.targetYawRad = computeTargetYaw(vehicle, currentWp);
        return setpoint;
    }

private:
    [[nodiscard]] Vector3D geoToNed(double latDeg, double lonDeg, float altM) const noexcept {
        constexpr double DegToRad = std::numbers::pi / 180.0;
        const double dLat = (latDeg - m_homeLat) * DegToRad;
        const double dLon = (lonDeg - m_homeLon) * DegToRad;
        const double latRad = m_homeLat * DegToRad;

        return Vector3D{
            static_cast<float>(dLat * EarthRadiusMeters),
            static_cast<float>(dLon * EarthRadiusMeters * std::cos(latRad)),
            -(altM - m_homeAlt)
        };
    }

    [[nodiscard]] bool isWaypointReached(const VehicleState& veh, const Waypoint& wp) const noexcept {
        const float distXY = veh.position.distance2D(m_currWpNed);
        const float distZ = std::abs(veh.position.z - m_currWpNed.z);

        // 1. Перевірка сфери досягнення
        if (distXY <= wp.acceptanceRadiusM && distZ <= (wp.acceptanceRadiusM * 1.5f)) {
            return true;
        }

        // 2. Перевірка площини прольоту (Passing Plane)
        const Vector3D dTarget{
            veh.position.x - m_currWpNed.x,
            veh.position.y - m_currWpNed.y,
            veh.position.z - m_currWpNed.z
        };
        const float sPass = dTarget.dot(m_segmentUnitIn);

        return (sPass >= 0.0f) && (distXY <= (wp.acceptanceRadiusM * 3.0f));
    }

    [[nodiscard]] float computeTargetYaw(const VehicleState& veh, const Waypoint& wp) const noexcept {
        if (m_roiNed.has_value()) {
            const float dx = m_roiNed->x - veh.position.x;
            const float dy = m_roiNed->y - veh.position.y;
            return std::atan2(dy, dx);
        }

        switch (wp.yawMode) {
        case YawMode::Fixed:
            return wp.yawTargetRad;
        case YawMode::Roi:
            if (m_roiNed.has_value()) {
                return std::atan2(m_roiNed->y - veh.position.y, m_roiNed->x - veh.position.x);
            }
            [[fallthrough]];
        case YawMode::AlongTrack:
        default: {
            const float dx = m_currWpNed.x - veh.position.x;
            const float dy = m_currWpNed.y - veh.position.y;
            return (std::sqrt(dx * dx + dy * dy) > 0.5f) ? std::atan2(dy, dx) : veh.yawRad;
        }
        }
    }

    std::span<const Waypoint> m_plan;
    double m_homeLat{0.0};
    double m_homeLon{0.0};
    float m_homeAlt{0.0f};

    size_t m_currentIndex{0};
    SequencerState m_state{SequencerState::Idle};
    float m_holdTimer{0.0f};

    Vector3D m_currWpNed{};
    Vector3D m_prevWpNed{};
    Vector3D m_segmentUnitIn{1.0f, 0.0f, 0.0f};
    std::optional<Vector3D> m_roiNed{std::nullopt};
};

} // namespace navigation
