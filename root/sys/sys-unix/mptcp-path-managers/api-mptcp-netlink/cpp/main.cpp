// C++23 Strongly Typed Enum Bitflags
#include <cstdint>

namespace mptcp::flags {
    enum class AddressFlag : std::uint32_t {
        Signal   = 1 << 0,
        Subflow  = 1 << 1,
        Backup   = 1 << 2,
        Fullmesh = 1 << 3,
        Implicit = 1 << 4
    };

    constexpr AddressFlag operator|(AddressFlag a, AddressFlag b) noexcept {
        return static_cast<AddressFlag>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b));
    }
}
