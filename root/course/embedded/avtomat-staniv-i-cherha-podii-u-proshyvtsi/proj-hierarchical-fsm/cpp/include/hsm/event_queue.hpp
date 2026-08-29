// event_queue.hpp — кільцева черга подій між перериваннями і головним циклом.
//
// Один виробник (переривання) і один споживач (головний цикл), тож
// блокування не потрібне: досить двох атомарних індексів із порядком
// release/acquire. Місткість — параметр шаблону, тому вся пам'ять черги
// статична і видна компоновнику ще до запуску.
#pragma once

#include "hsm/hsm.hpp"

#include <array>
#include <atomic>
#include <cstddef>
#include <optional>

namespace hsm {

template <std::size_t Capacity>
class EventQueue {
    static_assert(Capacity >= 2, "черга мусить мати щонайменше два слоти");

public:
    // Кладе подію. Викликається з переривання. false означає, що черга
    // повна: подію втрачено, і лічильник dropped() це зафіксував.
    bool push(const Event& e) noexcept {
        const std::size_t tail = tail_.load(std::memory_order_relaxed);
        const std::size_t next = advance(tail);
        if (next == head_.load(std::memory_order_acquire)) {
            // Затирати найстарішу подію не можна: саме там може лежати
            // сигнал аварії. Кажемо джерелу правду.
            dropped_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }
        buf_[tail] = e;
        tail_.store(next, std::memory_order_release);
        return true;
    }

    // Забирає найстарішу подію. Викликається з головного циклу.
    [[nodiscard]] std::optional<Event> pop() noexcept {
        const std::size_t head = head_.load(std::memory_order_relaxed);
        if (head == tail_.load(std::memory_order_acquire)) {
            return std::nullopt;
        }
        const Event e = buf_[head];
        head_.store(advance(head), std::memory_order_release);
        return e;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        const std::size_t head = head_.load(std::memory_order_acquire);
        const std::size_t tail = tail_.load(std::memory_order_acquire);
        return (tail + Capacity - head) % Capacity;
    }

    [[nodiscard]] std::size_t dropped() const noexcept {
        return dropped_.load(std::memory_order_relaxed);
    }

    // Один слот завжди лишається порожнім: саме він відрізняє повну чергу
    // від порожньої без окремого лічильника.
    [[nodiscard]] static constexpr std::size_t capacity() noexcept { return Capacity - 1; }

private:
    static constexpr std::size_t advance(std::size_t i) noexcept { return (i + 1) % Capacity; }

    std::array<Event, Capacity> buf_{};
    std::atomic<std::size_t> head_{0};
    std::atomic<std::size_t> tail_{0};
    std::atomic<std::size_t> dropped_{0};
};

} // namespace hsm
