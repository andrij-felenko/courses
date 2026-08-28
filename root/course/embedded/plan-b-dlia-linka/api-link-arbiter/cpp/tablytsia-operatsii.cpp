#include <span>
#include <string_view>
#include <expected>

namespace link_api {

enum class DriverError {
    HardwareFault,
    Busy,
    InvalidParameter,
    BufferOverflow
};

class IBearerDriver {
public:
    virtual ~IBearerDriver() = default;
    virtual std::expected<void, DriverError> init() noexcept = 0;
    virtual std::expected<size_t, DriverError> send(std::span<const uint8_t> data, QosPriority prio) noexcept = 0;
    virtual std::expected<size_t, DriverError> pollRx(std::span<uint8_t> buffer, BearerMetrics& outMetrics) noexcept = 0;
    virtual void setActive(bool active) noexcept = 0;
    virtual std::expected<void, DriverError> setFrequency(uint32_t freqHz) noexcept = 0;
};

struct BearerDescriptor {
    BearerId       id;
    std::string_view name;
    IBearerDriver *driver{nullptr};
    BearerMetrics  metrics{};
};

} // namespace link_api
