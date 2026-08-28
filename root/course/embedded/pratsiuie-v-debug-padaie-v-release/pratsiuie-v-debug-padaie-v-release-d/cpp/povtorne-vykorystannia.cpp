#include <cstdint>
#include <array>

void process_telemetry() {
    std::array<std::uint32_t, 16> raw_adc_data{};
    // Заповнення масиву
}

void transmit_packet() {
    std::uint32_t packet_flags = 0; // Обов'язкова ініціалізація
    if (packet_flags & 0x01U) {
        // Логіка обробки
    }
}

void task_loop() {
    process_telemetry();
    transmit_packet();
}
