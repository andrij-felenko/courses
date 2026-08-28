#include <cstdint>
#include <array>
#include <atomic>

std::array<std::uint8_t, 64> tx_buffer;
volatile std::uint32_t is_ready = 0;

void send_packet_safe() {
    tx_buffer[0] = 0xAA;
    tx_buffer[1] = 0xBB;
    
    // Ідіоматичний компіляторний бар'єр C++11 (не генерує інструкцій CPU)
    std::atomic_signal_fence(std::memory_order_release);
    
    is_ready = 1;
}
