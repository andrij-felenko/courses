#include <cstdint>
#include <concepts>
#include <span>
#include <optional>

namespace dataflow {

using FrameId = uint32_t;
using NodeId  = uint16_t;
using Port    = uint8_t;

enum class TokenFlags : uint8_t {
    None         = 0x00,
    EndOfStream  = 0x01,
    Acknowledge  = 0x02,
    ExceptionTrap= 0x04
};

struct Token {
    FrameId    frame_id{0};
    NodeId     node_id{0};
    Port       port{0};
    TokenFlags flags{TokenFlags::None};
    uint64_t   value{0};

    [[nodiscard]] constexpr bool is_ack() const noexcept {
        return (static_cast<uint8_t>(flags) & static_cast<uint8_t>(TokenFlags::Acknowledge)) != 0;
    }
};

} // namespace dataflow
