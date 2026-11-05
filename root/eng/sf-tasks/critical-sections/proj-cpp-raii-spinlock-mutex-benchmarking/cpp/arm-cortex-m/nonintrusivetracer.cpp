#include <cstdint>
#include <array>
#include <atomic>
#include "stm32f4xx.h"

template<std::size_t Capacity = 64>
class NonIntrusiveTracer {
public:
    struct EventRecord {
        uint32_t timestamp;
        uint32_t thread_id;
        uint8_t  event_code;
    };

private:
    std::array<EventRecord, Capacity> ring_buffer_{};
    std::atomic<uint32_t> write_head_{0};

public:
    void log_event(uint32_t thread_id, uint8_t event_code) noexcept {
        uint32_t idx = write_head_.fetch_add(1, std::memory_order_relaxed) % Capacity;
        ring_buffer_[idx] = EventRecord{
            .timestamp = DWT->CYCCNT,
            .thread_id = thread_id,
            .event_code = event_code
        };
    }

    [[nodiscard]] const EventRecord& get_record(std::size_t index) const noexcept {
        return ring_buffer_[index % Capacity];
    }
};
