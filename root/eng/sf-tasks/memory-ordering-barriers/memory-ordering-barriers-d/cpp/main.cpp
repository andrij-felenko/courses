#include <atomic>
#include <cstdint>

uint32_t         payload = 0;          // звичайні дані — без atomic
std::atomic<int> ready{0};             // прапорець-публікація

// Потік A — виробник
void produce() {
    payload = 42;                                  // 1) готуємо дані
    ready.store(1, std::memory_order_release);     // 2) публікуємо: release
    // release не дає запису payload просочитися ПІСЛЯ цього рядка
}

// Потік B — споживач
uint32_t consume() {
    while (ready.load(std::memory_order_acquire) == 0) {
        // чекаємо публікації; acquire не дає читанню payload
        // піднятися ВИЩЕ цієї перевірки
    }
    return payload;                                // гарантовано вже 42
}
