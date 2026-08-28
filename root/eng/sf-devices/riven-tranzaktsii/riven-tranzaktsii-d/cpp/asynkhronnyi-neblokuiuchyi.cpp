#include <functional>
#include <span>
#include <cstdint>

struct AsyncBusRequest {
    uint16_t                                  reg_addr{0};
    std::span<uint8_t>                        rx_buffer{};
    std::span<const uint8_t>                  tx_buffer{};
    std::move_only_function<void(bus::BusError)> callback{};
};
