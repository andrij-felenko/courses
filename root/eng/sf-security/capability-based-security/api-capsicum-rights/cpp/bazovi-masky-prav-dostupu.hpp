#include <cstdint>

namespace sel4 {

enum class CapRights : uint32_t {
    None        = 0,
    CanRead     = 1U << 0, /* Читання / отримання IPC */
    CanWrite    = 1U << 1, /* Запис / надсилання IPC */
    CanGrant    = 1U << 2, /* Передача повноважень через IPC */
    CanGrantReply = 1U << 3, /* Одноразова відповідь */
    AllRights   = CanRead | CanWrite | CanGrant | CanGrantReply
};

[[nodiscard]] constexpr CapRights operator|(CapRights a, CapRights b) noexcept {
    return static_cast<CapRights>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr CapRights operator&(CapRights a, CapRights b) noexcept {
    return static_cast<CapRights>(static_cast<uint32_t>(a) & static_cast<uint32_t>(b));
}

} // namespace sel4
