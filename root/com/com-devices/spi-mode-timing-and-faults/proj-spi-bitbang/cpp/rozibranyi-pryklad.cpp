#include <iostream>
#include <cstdint>
#include <array>
#include <optional>

struct JedecId {
    uint8_t manufacturer;
    uint8_t memory_type;
    uint8_t capacity;
};

template <SpiGpioPort Gpio>
std::optional<JedecId> read_flash_jedec_id(const SoftwareSpiMaster<Gpio>& spi) {
    const std::array<uint8_t, 4> tx_buffer{0x9F, 0xFF, 0xFF, 0xFF};
    std::array<uint8_t, 4> rx_buffer{0};

    spi.transfer(tx_buffer, rx_buffer);

    if (rx_buffer[1] == 0xEF) {
        return JedecId{
            .manufacturer = rx_buffer[1],
            .memory_type  = rx_buffer[2],
            .capacity     = rx_buffer[3]
        };
    }
    return std::nullopt;
}
