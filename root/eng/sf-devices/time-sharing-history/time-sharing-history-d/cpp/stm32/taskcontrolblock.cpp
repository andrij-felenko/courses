#include "stm32f4xx.h"
#include <cstdint>
#include <array>
#include <cstddef>

class TaskControlBlock {
public:
    static constexpr std::size_t kStackSizeWords = 256;

    struct ContextFrame {
        // Програмно збережені регістри
        uint32_t r4{0};
        uint32_t r5{0};
        uint32_t r6{0};
        uint32_t r7{0};
        uint32_t r8{0};
        uint32_t r9{0};
        uint32_t r10{0};
        uint32_t r11{0};

        // Апаратно збережені регістри при винятку
        uint32_t r0{0};
        uint32_t r1{0};
        uint32_t r2{0};
        uint32_t r3{0};
        uint32_t r12{0};
        uint32_t lr{0};
        uint32_t pc{0};
        uint32_t xpsr{0x01000000};
    };

    explicit TaskControlBlock(void (*entry_point)()) {
        // Встановлюємо покажчик стека на вершину масиву
        uint32_t* sp = stack_buffer_.data() + kStackSizeWords;
        sp -= (sizeof(ContextFrame) / sizeof(uint32_t));

        auto* frame = reinterpret_cast<ContextFrame*>(sp);
        frame->pc = reinterpret_cast<uint32_t>(entry_point);
        frame->xpsr = 0x01000000; // Режим Thumb ARM

        top_of_stack_ = sp;
    }

    [[nodiscard]] uint32_t* GetTopOfStack() const { return top_of_stack_; }
    void SetTopOfStack(uint32_t* sp) { top_of_stack_ = sp; }

private:
    uint32_t* top_of_stack_{nullptr};
    std::array<uint32_t, kStackSizeWords> stack_buffer_{};
};

class ContextSwitcher {
public:
    static void Switch(TaskControlBlock& current, TaskControlBlock& next) {
        // Оновлення покажчиків стека при виклику перемикання контексту
        TaskControlBlock* previous = &current;
        TaskControlBlock* active = &next;
        (void)previous;
        (void)active;
    }
};
