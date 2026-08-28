#include <cstdint>

// Концептуальний еквівалент функції маршрутизації вхідних пакетів у C++
namespace net::kernel_sim {
    struct SkBuff;
    struct NetDevice;

    int ip_route_input_noref(SkBuff* skb, std::uint32_t daddr, std::uint32_t saddr,
                             std::uint8_t tos, const NetDevice* dev) noexcept;
}
