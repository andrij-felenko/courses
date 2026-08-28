#include <cstdint>
#include <atomic>

// Ідіоматичний C++ для вбудованих систем: явні атомарні прапорці
static std::atomic<bool> packet_received{false};

extern "C" void USART1_IRQHandler() {
    // Асинхронний запис прапорця з бар'єром звільнення
    packet_received.store(true, std::memory_order_release);
}

void wait_for_data() {
    // std::atomic гарантує фізичне читання без кешування в регістрі
    while (!packet_received.load(std::memory_order_acquire)) {
        asm volatile("nop");
    }
}
