#include <cstdint>

// Змінна, спільна між головним циклом та обробником переривання
inline volatile std::uint32_t g_packet_counter{0};
inline volatile std::uint32_t g_device_flags{0};

void process_data() noexcept {
    // Наївний інкремент у фоновому потоці
    g_packet_counter = g_packet_counter + 1;
    
    // Наївне встановлення бітового прапорця
    g_device_flags = g_device_flags | (1U << 3);
}
