#include <cstdint>
#include <atomic>
#include <array>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

template <size_t SlotCount = 4>
class EmbeddedLongAdder {
public:
    static constexpr size_t AlignmentSize = 32;

    struct alignas(AlignmentSize) CounterSlot {
        std::atomic<int64_t> value{0};
    };

    EmbeddedLongAdder() noexcept {
        base_.store(0, std::memory_order_relaxed);
    }

    // Атомарне додавання значення
    void add(int64_t val) noexcept {
        int64_t expected = base_.load(std::memory_order_relaxed);
        
        if (base_.compare_exchange_weak(expected, expected + val, 
                                        std::memory_order_release, 
                                        std::memory_order_relaxed)) {
            return;
        }

        // Вирахування індексу на основі об'єкта задачі RTOS
        uint32_t slot_index = (reinterpret_cast<uintptr_t>(xTaskGetCurrentTaskHandle()) >> 3) % SlotCount;
        
        int64_t slot_expected = slots_[slot_index].value.load(std::memory_order_relaxed);
        while (!slots_[slot_index].value.compare_exchange_weak(slot_expected, 
                                                                slot_expected + val, 
                                                                std::memory_order_release, 
                                                                std::memory_order_relaxed)) {
            slot_index = (slot_index + 1) % SlotCount;
        }
    }

    // Отримання агрегованої суми
    [[nodiscard]] int64_t sum() const noexcept {
        int64_t total = base_.load(std::memory_order_acquire);
        for (const auto& slot : slots_) {
            total += slot.value.load(std::memory_order_acquire);
        }
        return total;
    }

private:
    alignas(AlignmentSize) std::atomic<int64_t> base_{0};
    std::array<CounterSlot, SlotCount> slots_;
};
