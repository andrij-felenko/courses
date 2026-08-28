// services/event_queue.hpp
#pragma once
#include <cstdint>
#include <array>
#include <optional>

namespace services {

enum class EventType : uint8_t {
    None,
    TimerTick,
    SensorTrigger,
    AlertThreshold,
    RadioTxComplete
};

struct Event {
    EventType type{EventType::None};
    uint32_t timestamp_ms{0};
    union {
        float sensor_val;
        int32_t error_code;
    } payload{0.0f};
};

template <size_t Capacity = 16>
class EventQueue {
public:
    EventQueue() : head_(0), tail_(0) {}

    bool push(const Event& evt) {
        size_t next = (head_ + 1) % Capacity;
        if (next == tail_) return false; // Черга переповнена
        buffer_[head_] = evt;
        head_ = next;
        return true;
    }

    std::optional<Event> pop() {
        if (tail_ == head_) return std::nullopt; // Черга порожня
        Event evt = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        return evt;
    }

private:
    std::array<Event, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
};

} // namespace services
