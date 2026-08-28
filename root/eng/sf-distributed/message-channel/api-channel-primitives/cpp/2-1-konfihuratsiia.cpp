#include <cstddef>
#include <cstdint>
#include <expected>
#include <memory>

struct ChannelConfig {
    std::size_t capacity{1024};
    std::size_t max_message_size{65536};
    std::uint32_t flags{0};
    std::uint32_t watermark_high{819};
    std::uint32_t watermark_low{205};
};

class MessageChannel;

[[nodiscard]] std::expected<std::unique_ptr<MessageChannel>, int>
open_channel(const ChannelConfig& config);
