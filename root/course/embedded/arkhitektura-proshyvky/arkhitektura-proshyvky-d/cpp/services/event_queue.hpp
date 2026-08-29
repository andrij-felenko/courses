// services/event_queue.hpp — черга подій між перериванням і головним циклом.
// Єдине місце системи, де ці два світи зустрічаються. Захист бере на себе
// hal::CriticalSection: секція закривається деструктором, тож жодна гілка
// виходу не може лишити переривання вимкненими.
#pragma once

#include "app/events.hpp"
#include "hal/critical_section.hpp"
#include "services/ring_buffer.hpp"

#include <cstdint>
#include <optional>

namespace services {

template <std::size_t Capacity>
class EventQueue final : public app::IEventSink {
public:
    // Публікація з головного циклу.
    bool post(const app::SystemEvent& event) override
    {
        const hal::CriticalSection guard;
        return push_locked(event);
    }

    // Публікація з обробника переривання. Тіло на Cortex-M те саме, але
    // назва окрема навмисно: у прошивці з ядром RTOS ці виклики різні,
    // і контекст має бути видно в місці виклику, а не в коментарі.
    bool post_from_isr(const app::SystemEvent& event)
    {
        const hal::CriticalSection guard;
        return push_locked(event);
    }

    [[nodiscard]] std::optional<app::SystemEvent> pop()
    {
        const hal::CriticalSection guard;
        return buffer_.pop();
    }

    [[nodiscard]] std::size_t size() const
    {
        const hal::CriticalSection guard;
        return buffer_.size();
    }

    // Скільки подій не влізло. Ненульове значення означає, що головний
    // цикл не встигає за перериваннями, і це видно в телеметрії.
    [[nodiscard]] std::uint32_t dropped() const noexcept { return dropped_; }

    // Найбільша зайнятість черги за час роботи: за нею вибирають місткість
    // замість того, щоб брати її зі стелі.
    [[nodiscard]] std::uint32_t high_water() const noexcept { return high_water_; }

private:
    bool push_locked(const app::SystemEvent& event)
    {
        if (!buffer_.push(event)) {
            ++dropped_;
            return false;
        }
        const auto used = static_cast<std::uint32_t>(buffer_.size());
        if (used > high_water_) {
            high_water_ = used;
        }
        return true;
    }

    RingBuffer<app::SystemEvent, Capacity> buffer_{};
    std::uint32_t                          dropped_{0};
    std::uint32_t                          high_water_{0};
};

} // namespace services
