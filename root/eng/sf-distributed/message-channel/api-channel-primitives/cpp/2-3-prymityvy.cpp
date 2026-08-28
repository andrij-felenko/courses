#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <vector>

struct ReceivedMessage {
    std::vector<std::byte> payload;
    std::uint64_t correlation_id{0};
    std::uint32_t message_type{0};
    std::uint64_t timestamp_ns{0};
};

class IChannelReceiver {
public:
    virtual ~IChannelReceiver() = default;
    virtual std::expected<ReceivedMessage, int> recv() = 0;
    virtual std::expected<std::optional<ReceivedMessage>, int> try_recv() = 0;
    virtual std::expected<ReceivedMessage, int> recv_timeout(std::chrono::milliseconds timeout) = 0;
};
