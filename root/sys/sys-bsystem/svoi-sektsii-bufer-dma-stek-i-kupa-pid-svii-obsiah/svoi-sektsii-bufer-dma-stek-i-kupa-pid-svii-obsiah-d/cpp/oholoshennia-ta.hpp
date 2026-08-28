#include <cstdint>
#include <array>
#include <span>
#include <bit>

namespace drivers {

inline constexpr std::size_t eth_rx_buffer_size = 1536;
inline constexpr std::size_t eth_rx_buf_count = 4;

struct alignas(32) DmaDescriptor {
    volatile std::uint32_t status{0};
    volatile std::uint32_t control{0};
    volatile std::uint32_t buffer_addr{0};
    volatile std::uint32_t next_desc{0};
};

// Буфери DMA у спеціалізованому домені RAM_D2
alignas(32) [[gnu::section(".dma_buffer")]]
static std::array<std::array<std::uint8_t, eth_rx_buffer_size>, eth_rx_buf_count> eth_rx_buffers;

alignas(32) [[gnu::section(".dma_buffer")]]
static std::array<DmaDescriptor, eth_rx_buf_count> dma_rx_ring;

// Змінна без ініціалізації для передачі стану через Reset
[[gnu::section(".noinit")]]
static std::uint32_t reset_reason_magic;

// Швидка математична функція в ITCM RAM
[[gnu::section(".ram_code"), gnu::noinline]]
float fast_inverse_sqrt(float x) noexcept {
    const float xhalf = 0.5f * x;
    std::uint32_t i = std::bit_cast<std::uint32_t>(x);
    i = 0x5f3759dfU - (i >> 1);
    float result = std::bit_cast<float>(i);
    result *= (1.5f - (xhalf * result * result));
    return result;
}

} // namespace drivers
