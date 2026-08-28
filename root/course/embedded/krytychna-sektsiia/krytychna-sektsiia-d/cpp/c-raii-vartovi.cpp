#include <cstdint>
#include <span>

// Помилка ручного керування в C++
int process_sensor_buffer(std::span<std::uint8_t> buffer) noexcept {
    const std::uint32_t primask = __get_PRIMASK();
    __disable_irq();
    
    if (buffer.empty()) {
        // Катастрофа: вихід без відновлення переривань
        return -1;
    }
    
    parse_data(buffer);
    
    __set_PRIMASK(primask);
    return 0;
}
