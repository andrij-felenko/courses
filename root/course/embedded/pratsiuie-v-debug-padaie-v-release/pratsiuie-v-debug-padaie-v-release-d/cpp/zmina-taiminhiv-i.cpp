#include <cstdint>
#include <span>

std::uint8_t rx_buffer[64];

void start_sensor_read() {
    dma_start_transfer(rx_buffer, sizeof(rx_buffer));
    
    // У Debug вбудовані перевірки й повільний код приховували проблему.
    // У Release parse_packet запускається миттєво і читає старі байти.
    parse_packet(std::span<const std::uint8_t, 64>{rx_buffer});
}
