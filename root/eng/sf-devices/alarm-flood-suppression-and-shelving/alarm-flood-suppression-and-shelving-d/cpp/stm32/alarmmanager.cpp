#include <cstdint>
#include <array>
#include <atomic>
#include <span>
#include "stm32f4xx.h"

template <std::size_t AlarmCount, std::size_t QueueSize>
class AlarmManager {
public:
    using Bitmask = std::uint32_t;
    static_assert(AlarmCount <= 32, "Дана реалізація підтримує до 32 тривог");

    struct AlarmEvent {
        std::uint16_t alarm_id{0};
        std::uint8_t  state{0};
        std::uint32_t timestamp_us{0};
    };

    constexpr AlarmManager() noexcept : head_(0), tail_(0), active_in_queue_(0), raw_vector_(0), shelved_vector_(0), final_vector_(0), current_mode_(0) {}

    // Встановлення матриці суміжності графу причинності
    constexpr void setAdjacencyRow(std::size_t alarm_id, Bitmask child_mask) noexcept {
        if (alarm_id < AlarmCount) {
            adj_matrix_[alarm_id] = child_mask;
        }
    }

    // Встановлення маски режиму FSM
    constexpr void setModeMask(std::size_t mode_id, Bitmask mask) noexcept {
        if (mode_id < mode_masks_.size()) {
            mode_masks_[mode_id] = mask;
        }
    }

    // Додавання події з контексту переривання ISR з дедуплікацією
    [[nodiscard]] bool pushEventFromISR(std::uint16_t alarm_id, std::uint8_t state) noexcept {
        if (alarm_id >= AlarmCount) {
            return false;
        }

        const Bitmask mask = (1U << alarm_id);
        if ((active_in_queue_.load(std::memory_order_relaxed) & mask) != 0U) {
            return false; // Подія дедуплікована
        }

        const std::uint32_t curr_head = head_.load(std::memory_order_relaxed);
        const std::uint32_t next_head = (curr_head + 1U) % QueueSize;
        const std::uint32_t curr_tail = tail_.load(std::memory_order_acquire);

        if (next_head == curr_tail) {
            return false; // Переповнення кільцевого буфера
        }

        buffer_[curr_head] = AlarmEvent{
            .alarm_id = alarm_id,
            .state = state,
            .timestamp_us = DWT->CYCCNT / (SystemCoreClock / 1000000U)
        };

        active_in_queue_.fetch_or(mask, std::memory_order_relaxed);
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    // Фонова обробка вектора тривог у такті RTOS
    void processCycle() noexcept {
        std::uint32_t curr_tail = tail_.load(std::memory_order_relaxed);
        const std::uint32_t curr_head = head_.load(std::memory_order_acquire);

        while (curr_tail != curr_head) {
            const auto& evt = buffer_[curr_tail];
            const Bitmask mask = (1U << evt.alarm_id);

            if (evt.state != 0U) {
                raw_vector_ |= mask;
            } else {
                raw_vector_ &= ~mask;
            }

            active_in_queue_.fetch_and(~mask, std::memory_order_relaxed);
            curr_tail = (curr_tail + 1U) % QueueSize;
        }
        tail_.store(curr_tail, std::memory_order_release);

        const Bitmask mode_mask = mode_masks_[current_mode_];
        const Bitmask candidates = raw_vector_ & mode_mask & ~shelved_vector_;

        Bitmask suppress_mask = 0U;
        Bitmask temp_cand = candidates;

        while (temp_cand != 0U) {
            const std::uint32_t bit_index = 31U - static_cast<std::uint32_t>(__builtin_clz(temp_cand));
            suppress_mask |= adj_matrix_[bit_index];
            temp_cand &= ~(1U << bit_index);
        }

        final_vector_ = candidates & ~suppress_mask;
    }

    [[nodiscard]] Bitmask getFinalVector() const noexcept { return final_vector_; }
    void setMode(std::size_t mode) noexcept { if (mode < mode_masks_.size()) current_mode_ = mode; }

private:
    alignas(4) std::array<AlarmEvent, QueueSize> buffer_{};
    std::atomic<std::uint32_t> head_{0};
    std::atomic<std::uint32_t> tail_{0};
    std::atomic<Bitmask> active_in_queue_{0};

    std::array<Bitmask, AlarmCount> adj_matrix_{};
    std::array<Bitmask, 4> mode_masks_{};
    Bitmask raw_vector_{0};
    Bitmask shelved_vector_{0};
    Bitmask final_vector_{0};
    std::size_t current_mode_{0};
};
