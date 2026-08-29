// services/dispatcher.hpp — диспетчер подій.
// Джерело події не знає обробника, обробник не знає джерела: між ними лише черга
// й маска типів. Таблиця підписників статична, купа не задіяна взагалі.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <initializer_list>

#include "services/event_queue.hpp"

namespace services {

class EventMask {
public:
    constexpr EventMask() = default;

    constexpr explicit EventMask(EventType type) : bits_(bit(type)) {}

    constexpr EventMask(std::initializer_list<EventType> types)
    {
        for (const EventType t : types) {
            bits_ |= bit(t);
        }
    }

    constexpr bool contains(EventType type) const { return (bits_ & bit(type)) != 0u; }
    constexpr bool empty() const { return bits_ == 0u; }

private:
    static constexpr std::uint32_t bit(EventType type)
    {
        return 1u << static_cast<std::uint32_t>(type);
    }

    std::uint32_t bits_{0};
};

// Вихід для того, хто події породжує. Бізнес-логіка знає лише цей інтерфейс,
// тому не залежить від ємності черги й узагалі від того, що це черга.
class IEventSink {
public:
    virtual ~IEventSink() = default;

    IEventSink() = default;
    IEventSink(const IEventSink&) = delete;
    IEventSink& operator=(const IEventSink&) = delete;

    virtual bool publish(const Event& evt) = 0;
};

// Перехідник від інтерфейсу до конкретної кільцевої черги.
template <class Queue>
class QueueSink final : public IEventSink {
public:
    explicit QueueSink(Queue& queue) noexcept : queue_(queue) {}

    bool publish(const Event& evt) override { return queue_.push(evt); }

private:
    Queue& queue_;
};

class IEventHandler {
public:
    virtual ~IEventHandler() = default;

    IEventHandler() = default;
    IEventHandler(const IEventHandler&) = delete;
    IEventHandler& operator=(const IEventHandler&) = delete;

    virtual void on_event(const Event& evt) = 0;
};

template <class Queue, std::size_t MaxSubscribers = 8>
class Dispatcher {
public:
    explicit Dispatcher(Queue& queue) noexcept : queue_(queue) {}

    // Повертає false, коли статичну таблицю вичерпано: мовчки нарощувати її
    // нема з чого — динамічної памʼяті в прошивці немає.
    bool subscribe(EventMask mask, IEventHandler& handler)
    {
        if (mask.empty() || count_ >= MaxSubscribers) {
            return false;
        }
        subscribers_[count_] = Subscriber{mask, &handler};
        ++count_;
        return true;
    }

    bool run_once()
    {
        const std::optional<Event> evt = queue_.pop();
        if (!evt) {
            return false;
        }

        bool taken = false;
        for (std::size_t i = 0; i < count_; ++i) {
            if (subscribers_[i].mask.contains(evt->type)) {
                subscribers_[i].handler->on_event(*evt);
                taken = true;
            }
        }

        if (taken) {
            ++handled_;
        } else {
            ++unhandled_;
        }
        return true;
    }

    // Обробник має право покласти в чергу нову подію (тривога породжує скидання
    // живлення), тому цикл іде до справжнього спорожнення, а не на знімок довжини.
    std::size_t drain()
    {
        std::size_t processed = 0;
        const std::size_t limit = Queue::capacity() * 4u;
        while (run_once()) {
            if (++processed >= limit) {
                break;  // Запобіжник від нескінченного самопородження подій
            }
        }
        return processed;
    }

    std::size_t handled() const noexcept { return handled_; }
    std::size_t unhandled() const noexcept { return unhandled_; }

private:
    struct Subscriber {
        EventMask mask{};
        IEventHandler* handler{nullptr};
    };

    Queue& queue_;
    std::array<Subscriber, MaxSubscribers> subscribers_{};
    std::size_t count_{0};
    std::size_t handled_{0};
    std::size_t unhandled_{0};
};

}  // namespace services
