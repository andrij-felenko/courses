#include <cstdint>
#include <string>
#include <string_view>
#include <array>

namespace katran {

enum class Protocol : uint8_t {
    Tcp = 6,
    Udp = 17
};

enum class VipFlags : uint32_t {
    DirectServerReturn = 1 << 0,
    GenericUdpEncapsulation = 1 << 1,
    IpInIp = 2 << 2,
    QuicConnectionIdRouting = 1 << 3
};

struct VipDefinition {
    uint32_t vip{0};
    uint16_t port{0};
    Protocol proto{Protocol::Tcp};
    uint8_t flags{0};
};

struct VipMeta {
    VipFlags flags{VipFlags::DirectServerReturn};
    uint32_t table_size{65537};
    uint32_t vip_num{0};
};

struct RealDefinition {
    uint32_t address{0};
    uint32_t flags{0};
    uint16_t port{0};
    uint8_t weight{1};
    uint8_t pad{0};
};

struct FlowKey {
    uint32_t src{0};
    uint32_t dst{0};
    uint16_t src_port{0};
    uint16_t dst_port{0};
    Protocol proto{Protocol::Tcp};
    std::array<uint8_t, 3> pad{};
};

struct FlowValue {
    uint32_t backend_idx{0};
    uint64_t last_seen_ns{0};
};

} // namespace katran
