#pragma once

#include <cstdint>
#include <atomic>
#include <compare>
#include <new>
#include <string>
#include <string_view>
#include <expected>
#include <format>

namespace distributed {

#ifdef __cpp_lib_hardware_interference_size
using std::hardware_destructive_interference_size;
#else
constexpr size_t hardware_destructive_interference_size = 64;
#endif

/**
 * @brief Незмінний кортеж мітки часу Лампорта з підтримкою тристороннього порівняння C++20.
 */
struct LamportTimestamp {
    uint32_t node_id{0};
    uint64_t counter{0};

    [[nodiscard]] constexpr auto operator<=>(const LamportTimestamp& other) const noexcept {
        if (auto cmp = counter <=> other.counter; cmp != 0) return cmp;
        return node_id <=> other.node_id;
    }

    [[nodiscard]] constexpr bool operator==(const LamportTimestamp& other) const noexcept = default;

    [[nodiscard]] std::string to_header_string() const {
        return std::format("{}:{}", counter, node_id);
    }
};

/**
 * @brief Потокобезпечний логічний годинник Лампорта на базі атомарних операцій.
 */
class alignas(hardware_destructive_interference_size) LamportClock {
public:
    explicit LamportClock(uint32_t node_id, uint64_t initial_counter = 0) noexcept
        : node_id_(node_id), counter_(initial_counter) {}

    LamportClock(const LamportClock&) = delete;
    LamportClock& operator=(const LamportClock&) = delete;
    LamportClock(LamportClock&&) = delete;
    LamportClock& operator=(LamportClock&&) = delete;

    /**
     * @brief Фіксує локальну подію: виконує fetch_add(1) з семантикою acquire-release.
     */
    [[nodiscard]] LamportTimestamp tick() noexcept {
        const uint64_t next = counter_.fetch_add(1, std::memory_order_acq_rel) + 1;
        return LamportTimestamp{.node_id = node_id_, .counter = next};
    }

    /**
     * @brief Формує мітку для відправлення повідомлення.
     */
    [[nodiscard]] LamportTimestamp send_event() noexcept {
        return tick();
    }

    /**
     * @brief Оновлює лічильник за правилом max(current, incoming) + 1 через CAS-цикл.
     */
    [[nodiscard]] LamportTimestamp recv_event(uint64_t incoming_counter) noexcept {
        uint64_t current = counter_.load(std::memory_order_relaxed);
        uint64_t next = 0;
        do {
            next = (current > incoming_counter ? current : incoming_counter) + 1;
        } while (!counter_.compare_exchange_weak(
            current, next, std::memory_order_acq_rel, std::memory_order_relaxed));

        return LamportTimestamp{.node_id = node_id_, .counter = next};
    }

    [[nodiscard]] uint32_t node_id() const noexcept { return node_id_; }

    [[nodiscard]] uint64_t read_current() const noexcept {
        return counter_.load(std::memory_order_acquire);
    }

private:
    const uint32_t node_id_;
    std::atomic<uint64_t> counter_;
};

} // namespace distributed
