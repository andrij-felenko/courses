#include <cstdint>
#include <variant>
#include <optional>
#include <expected>

namespace drone::payload {

// Типи дій корисного навантаження
enum class ActionStatus : uint8_t {
    Idle = 0,
    Running,
    Completed,
    Failed
};

enum class ActionError : uint8_t {
    InvalidParameter,
    HardwareFault,
    Timeout,
    Busy
};

struct CameraDistanceConfig {
    float distance_interval_m{0.0f};
};

struct RoiTargetLocation {
    double latitude{0.0};
    double longitude{0.0};
    float altitude_m{0.0f};
};

struct CargoReleaseConfig {
    uint16_t release_timeout_ms{400};
    uint8_t  retry_limit{3};
};

struct ShutterPulseCommand {};
struct ClearRoiCommand {};

using MissionPayloadAction = std::variant<
    ShutterPulseCommand,
    CameraDistanceConfig,
    RoiTargetLocation,
    ClearRoiCommand,
    CargoReleaseConfig
>;

class IPayloadSubsystem {
public:
    virtual ~IPayloadSubsystem() = default;
    virtual std::expected<void, ActionError> executeAction(const MissionPayloadAction& action) = 0;
    virtual ActionStatus getActionStatus() const noexcept = 0;
    virtual void processPeriodic50Hz() noexcept = 0;
};

} // namespace drone::payload
