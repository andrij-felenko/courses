#include <memory>
#include <expected>
#include <string_view>

namespace truetime {

struct TimeSample {
    Nanoseconds utc_time{0};
    Nanoseconds reference_error{0};
};

enum class DriverError : std::uint8_t {
    DeviceNotAvailable,
    SignalLost,
    InvalidMeasurement,
    HardwareFault
};

class IHardwareDriver {
public:
    virtual ~IHardwareDriver() = default;

    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    virtual std::expected<void, DriverError> initialize() = 0;
    [[nodiscard]] virtual std::expected<TimeSample, DriverError> poll_sample() = 0;
    virtual std::expected<void, DriverError> adjust_frequency(double offset_ppb) = 0;
    virtual void shutdown() noexcept = 0;
};

} // namespace truetime
