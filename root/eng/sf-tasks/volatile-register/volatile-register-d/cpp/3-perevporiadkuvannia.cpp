#include <cstdint>
#include <array>

std::array<std::uint8_t, 64> tx_buffer;  // Звичайний буфер (не volatile)
volatile std::uint32_t is_ready = 0;     // Прапорець готовності

void send_packet() {
    tx_buffer[0] = 0xAA;                 // 1. Запис корисних даних
    tx_buffer[1] = 0xBB;
    is_ready = 1;                        // 2. Сигнал обробнику переривання
}
