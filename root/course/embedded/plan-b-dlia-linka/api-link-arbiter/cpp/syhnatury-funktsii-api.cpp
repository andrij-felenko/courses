#include <functional>

namespace link_api {

using SwitchCallback   = std::function<void(BearerId prevBearer, BearerId newBearer, ArbiterState state)>;
using AutonomyCallback = std::function<void(std::chrono::milliseconds silentDuration)>;

class ILinkArbiterManager {
public:
    virtual ~ILinkArbiterManager() = default;
    virtual std::expected<void, DriverError> initialize(const ArbiterConfig& config) noexcept = 0;
    virtual std::expected<void, DriverError> registerBearer(const BearerDescriptor& bearer) noexcept = 0;
    virtual std::expected<size_t, DriverError> transmit(std::span<const uint8_t> payload, QosPriority prio) noexcept = 0;
    virtual void tick(std::chrono::milliseconds now) noexcept = 0;
    virtual ArbiterState currentState() const noexcept = 0;
    virtual BearerId activeBearerId() const noexcept = 0;
    virtual void setSwitchCallback(SwitchCallback cb) noexcept = 0;
    virtual void setAutonomyCallback(AutonomyCallback cb) noexcept = 0;
};

} // namespace link_api
