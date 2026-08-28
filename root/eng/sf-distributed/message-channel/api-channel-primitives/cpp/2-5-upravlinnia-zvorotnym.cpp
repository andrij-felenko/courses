#include <cstdint>
#include <expected>

enum class FlowSignal : std::uint8_t {
    Resume = 0,
    Pause  = 1
};

struct ChannelMetrics {
    std::uint64_t messages_sent{0};
    std::uint64_t messages_received{0};
    std::uint64_t bytes_transferred{0};
    std::uint32_t current_depth{0};
    std::uint32_t waiting_producers{0};
    std::uint32_t waiting_consumers{0};
    std::uint64_t high_watermark_hits{0};
};

class IChannelDiagnostics {
public:
    virtual ~IChannelDiagnostics() = default;
    virtual std::expected<void, int> set_flow(FlowSignal signal) = 0;
    [[nodiscard]] virtual ChannelMetrics get_metrics() const = 0;
};
