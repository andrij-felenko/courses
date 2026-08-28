#include <cstdint>
#include <array>

void process_step_a() {
    std::array<std::uint8_t, 256> temp_buf{};
    // Обробка...
}

void process_step_b() {
    std::array<std::uint8_t, 256> temp_buf{};
    // Обробка...
}

void worker_task() {
    while (true) {
        process_step_a();
        process_step_b();
    }
}
