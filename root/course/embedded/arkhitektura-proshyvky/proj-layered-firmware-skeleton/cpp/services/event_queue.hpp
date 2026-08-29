// services/event_queue.hpp — кільцева черга подій.
// Шаблон цілком у заголовку: компілятор вбудовує обидві операції в місце виклику,
// тож брокер повідомлень не коштує жодного зайвого переходу.
#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <optional>
#include <variant>

#include "hal/critical_section.hpp"

namespace services {

enum class EventType : std::uint8_t {
    None = 0,
    TimerTick,        // Періодичний тик від SysTick
    SensorTrigger,    // Час опитати давач
    AlertThreshold,   // Температура перевищила поріг тривоги
    SensorFault,      // Давач не відповідає кілька спроб поспіль
    RadioTxComplete,  // Передавач звільнився
};

// Корисне навантаження — розмічене обʼєднання замість безтипового void*:
// тип payload перевіряє компілятор, а не коментар біля union.
using EventPayload = std::variant<std::monostate, float, std::int32_t>;

struct Event {
    EventType type{EventType::None};
    std::chrono::milliseconds timestamp{0};
    EventPayload payload{};
};

template <std::size_t Capacity = 16>
class EventQueue {
    static_assert(Capacity >= 2, "кільце на одну комірку не відрізняє порожнє від повного");

public:
    // Push кличуть і головний цикл, і обробники переривань: тут не один виробник,
    // тому індекси правляться під критичною секцією, а не позначаються volatile —
    // volatile упорядковує доступ до памʼяті, але неподільності не дає.
    bool push(const Event& evt)
    {
        const hal::CriticalSection guard;

        const std::size_t next = (head_ + 1u) % Capacity;
        if (next == tail_) {
            if (dropped_ != std::numeric_limits<std::uint16_t>::max()) {
                ++dropped_;  // Мовчазна втрата гірша за втрату, яку видно в діагностиці
            }
            return false;
        }
        buffer_[head_] = evt;
        head_ = next;
        return true;
    }

    std::optional<Event> pop()
    {
        const hal::CriticalSection guard;

        if (tail_ == head_) {
            return std::nullopt;
        }
        Event evt = buffer_[tail_];
        tail_ = (tail_ + 1u) % Capacity;
        return evt;
    }

    bool empty() const
    {
        const hal::CriticalSection guard;
        return head_ == tail_;
    }

    std::size_t size() const
    {
        const hal::CriticalSection guard;
        return (head_ + Capacity - tail_) % Capacity;
    }

    static constexpr std::size_t capacity() noexcept { return Capacity; }

    std::uint16_t dropped() const noexcept { return dropped_; }

private:
    std::array<Event, Capacity> buffer_{};
    std::size_t head_{0};
    std::size_t tail_{0};
    std::uint16_t dropped_{0};
};

}  // namespace services
