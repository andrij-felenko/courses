#include <cstdint>

enum class Perm : std::uint8_t {
    None    = 0,
    Exec    = 1U << 0,
    Write   = 1U << 1,
    Read    = 1U << 2,
    ReadWrite = Read | Write,
    All     = Read | Write | Exec
};

[[nodiscard]] constexpr Perm operator|(Perm a, Perm b) noexcept {
    return static_cast<Perm>(static_cast<std::uint8_t>(a) | static_cast<std::uint8_t>(b));
}

[[nodiscard]] constexpr Perm operator&(Perm a, Perm b) noexcept {
    return static_cast<Perm>(static_cast<std::uint8_t>(a) & static_cast<std::uint8_t>(b));
}

[[nodiscard]] constexpr bool has_all_permissions(Perm user, Perm required) noexcept {
    return (user & required) == required;
}
