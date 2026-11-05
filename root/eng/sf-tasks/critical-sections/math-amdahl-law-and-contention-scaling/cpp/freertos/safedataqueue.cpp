#include <cstdint>
#include <atomic>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Потокобезпечна черга даних на C++11 із захистом атомарним прапорцем
class SafeDataQueue {
private:
    static constexpr size_t BUFFER_SIZE = 256;
    uint8_t buffer_[BUFFER_SIZE];
    size_t head_{0};
    size_t tail_{0};
    std::atomic_flag lock_flag_ = ATOMIC_FLAG_INIT;

public:
    SafeDataQueue() = default;

    // Захоплення спін-замка на атомарному прапорці
    void lock() {
        while (lock_flag_.test_and_set(std::memory_order_acquire)) {
            // Активне очікування на спін-замку
#if defined(__ARM_ARCH)
            __asm__ volatile("yield"); // Зниження енергоспоживання ядра ARM
#endif
        }
    }

    // Звільнення спін-замка
    void unlock() {
        lock_flag_.clear(std::memory_order_release);
    }

    // Вставка елемента у буфер
    bool push(uint8_t byte) {
        lock(); // Початок критичної секції
        size_t next_head = (head_ + 1) % BUFFER_SIZE;
        if (next_head == tail_) {
            unlock();
            return false;
        }
        buffer_[head_] = byte;
        head_ = next_head;
        unlock(); // Кінець критичної секції
        return true;
    }
};
