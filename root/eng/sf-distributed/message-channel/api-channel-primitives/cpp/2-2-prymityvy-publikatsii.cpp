#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

struct OutgoingMessage {
    std::span<const std::byte> payload;
    std::uint64_t correlation_id{0};
    std::uint32_t message_type{0};
    std::uint32_t flags{0};
};

class IChannelSender {
public:
    virtual ~IChannelSender() = default;
    virtual std::expected<void, int> send(const OutgoingMessage& msg) = 0;
    virtual std::expected<void, int> try_send(const OutgoingMessage& msg) = 0;
    virtual std::expected<void, int> send_timeout(const OutgoingMessage& msg, std::chrono::milliseconds timeout) = 0;
};
