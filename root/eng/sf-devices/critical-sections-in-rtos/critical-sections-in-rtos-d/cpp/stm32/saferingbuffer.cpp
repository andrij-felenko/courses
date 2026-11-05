#include "FreeRTOS.h"
#include "task.h"
#include <array>
#include <cstdint>

template <typename T, std::size_t Capacity>
class SafeRingBuffer {
public:
    SafeRingBuffer() : head_(0), tail_(0) {}

    bool pushFromTask(const T& item) {
        bool result = false;

        // Використання критичної секції в контексті задачі
        taskENTER_CRITICAL();
        std::size_t next_head = (head_ + 1) % Capacity;
        if (next_head != tail_) {
            buffer_[head_] = item;
            head_ = next_head;
            result = true;
        }
        taskEXIT_CRITICAL();

        return result;
    }

    bool pushFromIsr(const T& item) {
        bool result = false;

        // Безпечний захист у контексті переривання ISR
        UBaseType_t saved_status = taskENTER_CRITICAL_FROM_ISR();
        std::size_t next_head = (head_ + 1) % Capacity;
        if (next_head != tail_) {
            buffer_[head_] = item;
            head_ = next_head;
            result = true;
        }
        taskEXIT_CRITICAL_FROM_ISR(saved_status);

        return result;
    }

private:
    std::array<T, Capacity> buffer_;
    volatile std::size_t head_;
    volatile std::size_t tail_;
};
