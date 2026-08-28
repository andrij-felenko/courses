#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

struct IoVectorChunk {
    std::span<const std::byte> data;
};

struct VectorizedMessage {
    std::span<const IoVectorChunk> chunks;
    std::uint64_t correlation_id{0};
    std::uint32_t message_type{0};
};

class IVectorizedChannel {
public:
    virtual ~IVectorizedChannel() = default;
    virtual std::expected<void, int> send_iov(const VectorizedMessage& msg) = 0;
    virtual std::expected<std::size_t, int> recv_iov(std::span<std::span<std::byte>> buffers) = 0;
};
