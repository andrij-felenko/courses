#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace iot {

struct TelemetryEntry {
    std::uint32_t timestamp{0};
    float measuredTemperature{0.0F};
    std::uint16_t currentPowerWatts{0};
    bool heatingActive{false};
    bool fromOfflineCache{false}; /* вимір зроблено без каналу й пролежав у буфері */
};

/*
 * Кільцевий буфер на статичній пам'яті: розмір відомий на етапі компіляції,
 * купи в цьому проєкті немає взагалі.
 */
template <std::size_t Capacity = 32>
class TelemetryQueue {
    static_assert(Capacity > 1, "черга на один елемент не переживе жодного обриву");

public:
    /* true — буфер був повний і найстаріший вимір затерто. */
    bool push(const TelemetryEntry& entry) noexcept
    {
        bool overwrote = false;

        slots_[head_] = entry;
        head_ = (head_ + 1) % Capacity;

        if (count_ < Capacity) {
            ++count_;
        } else {
            /* Пам'ять скінчилася раніше за обрив: свіжий вимір цінніший за вчорашній. */
            tail_ = (tail_ + 1) % Capacity;
            ++dropped_;
            overwrote = true;
        }
        return overwrote;
    }

    /* Найстаріший звіт без вилучення: передача може не вдатися,
       і тоді вилучати його не можна. */
    [[nodiscard]] const TelemetryEntry* front() const noexcept
    {
        return (count_ == 0) ? nullptr : &slots_[tail_];
    }

    void pop() noexcept
    {
        if (count_ == 0) {
            return;
        }
        tail_ = (tail_ + 1) % Capacity;
        --count_;
    }

    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }
    [[nodiscard]] std::uint32_t droppedTotal() const noexcept { return dropped_; }
    [[nodiscard]] static constexpr std::size_t capacity() noexcept { return Capacity; }

private:
    std::array<TelemetryEntry, Capacity> slots_{};
    std::size_t head_{0};
    std::size_t tail_{0};
    std::size_t count_{0};
    std::uint32_t dropped_{0};
};

} // namespace iot
