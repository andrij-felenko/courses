#include <cstdint>
#include <array>
#include <memory_resource>
#include <vector>

namespace memory {

// Фіксований буфер у спеціалізованому домені RAM_D2
alignas(32) [[gnu::section(".dma_buffer")]]
static std::array<std::byte, 16384> telemetry_dma_pool;

void process_sensor_packet() {
    // Монотонний алокатор, що працює виключно всередині масиву telemetry_dma_pool
    std::pmr::monotonic_buffer_resource pool_resource(
        telemetry_dma_pool.data(),
        telemetry_dma_pool.size(),
        std::pmr::null_memory_resource() // Заборона звернення до глобальної купи
    );

    // Вектор гарантовано розміщується у виділеному домені RAM_D2
    std::pmr::vector<std::uint32_t> packet_data(&pool_resource);
    packet_data.reserve(512);

    for (std::uint32_t i = 0; i < 256; ++i) {
        packet_data.push_back(i * 15U);
    }

    // При виході з функції вся пам'ять звільняється миттєвим скиданням покажчика
}

} // namespace memory
