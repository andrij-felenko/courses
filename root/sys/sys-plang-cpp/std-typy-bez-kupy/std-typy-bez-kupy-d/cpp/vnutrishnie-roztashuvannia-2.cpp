#include <array>
#include <cstdint>

// 1. Повністю у Flash-пам'яті (.rodata), 0 байтів ОЗП
constexpr std::array<uint8_t, 4> CRC_TABLE = {0x00, 0x5E, 0xBC, 0xE2};

// 2. У секції .bss статичного ОЗП мікроконтролера
static std::array<uint8_t, 256> dma_uart_rx_buffer;

void process_data() {
    // 3. На стеку функції (звільняється автоматично при виході)
    std::array<uint16_t, 8> adc_samples{};
    adc_samples.fill(0);
}
