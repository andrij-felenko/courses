#include <cstdint>
#include <array>
#include <span>
#include <string_view>

namespace net::stun {

inline constexpr uint32_t MAGIC_COOKIE = 0x2112A442;
inline constexpr uint16_t MAGIC_COOKIE_HIGH16 = 0x2112;

enum class MessageClass : uint16_t {
    Request      = 0b00,
    Indication   = 0b01,
    SuccessResp  = 0b10,
    ErrorResp    = 0b11
};

enum class Method : uint16_t {
    Binding          = 0x001,
    Allocate         = 0x003,
    Refresh          = 0x004,
    Send             = 0x006,
    Data             = 0x007,
    CreatePermission = 0x008,
    ChannelBind      = 0x009
};

enum class AttributeType : uint16_t {
    MappedAddress     = 0x0001,
    Username          = 0x0006,
    MessageIntegrity  = 0x0008,
    ErrorCode         = 0x0009,
    ChannelNumber     = 0x000C,
    Lifetime          = 0x000D,
    XorPeerAddress    = 0x0012,
    Data              = 0x0013,
    XorRelayedAddress = 0x0016,
    EvenPort          = 0x0018,
    RequestedTransport= 0x0019,
    DontFragment      = 0x001A,
    XorMappedAddress  = 0x0020,
    ReservationToken  = 0x0022,
    Software          = 0x8022,
    AlternateServer   = 0x8023,
    Fingerprint       = 0x8028
};

#pragma pack(push, 1)
struct Header {
    uint16_t msg_type;
    uint16_t msg_length;
    uint32_t magic_cookie;
    std::array<uint8_t, 12> transaction_id;

    [[nodiscard]] constexpr MessageClass getClass() const noexcept {
        uint16_t c1 = (msg_type >> 8) & 0x01;
        uint16_t c0 = (msg_type >> 4) & 0x01;
        return static_cast<MessageClass>((c1 << 1) | c0);
    }

    [[nodiscard]] constexpr uint16_t getMethod() const noexcept {
        return (msg_type & 0x000F) | ((msg_type >> 1) & 0x0070) | ((msg_type >> 2) & 0x0F80);
    }
};

struct XorAddressIpv4 {
    uint8_t  reserved{0};
    uint8_t  family{0x01};
    uint16_t x_port{0};
    uint32_t x_address{0};

    [[nodiscard]] constexpr uint16_t decodePort() const noexcept {
        return x_port ^ MAGIC_COOKIE_HIGH16;
    }

    [[nodiscard]] constexpr uint32_t decodeAddress() const noexcept {
        return x_address ^ MAGIC_COOKIE;
    }
};

struct ChannelDataHeader {
    uint16_t channel_number;
    uint16_t length;
};
#pragma pack(pop)

} // namespace net::stun
