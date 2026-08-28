#include <cstdint>
#include <variant>

enum class EventId : uint8_t {
    SysNone             = 0x00,
    SysEntry            = 0x01,
    SysExit             = 0x02,
    SysInit             = 0x03,
    CmdStartMission     = 0x10,
    CmdPauseMission     = 0x11,
    CmdResumeMission    = 0x12,
    CmdAbortMission     = 0x13,
    NavWaypointReached  = 0x20,
    NavHeadingLocked    = 0x21,
    NavObstacleNear     = 0x22,
    NavObstacleStop     = 0x23,
    NavPathClear        = 0x24,
    FailBatteryLow      = 0x40,
    FailSensorTimeout   = 0x41,
    FailActuatorStall   = 0x42,
    FailCritical        = 0x4F
};

struct Point2D {
    int16_t x_mm{0};
    int16_t y_mm{0};
};

struct FaultInfo {
    uint16_t sensor_id{0};
    uint16_t error_code{0};
};

using EventPayload = std::variant<std::monostate, int32_t, float, uint32_t, Point2D, FaultInfo>;

struct Event {
    EventId id{EventId::SysNone};
    uint8_t priority{128};
    uint32_t timestamp_us{0};
    EventPayload param{};
};
