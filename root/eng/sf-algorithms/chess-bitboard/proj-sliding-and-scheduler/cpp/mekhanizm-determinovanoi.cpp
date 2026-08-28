#include <cstdint>
#include <array>
#include <bit>
#include <optional>
#include <cassert>

class O1TaskScheduler {
public:
    static constexpr size_t PriorityLevels = 64;

    struct Task {
        Task* prev{nullptr};
        Task* next{nullptr};
        uint32_t task_id{0};
        uint8_t priority{0};
    };

    O1TaskScheduler() noexcept = default;

    void enqueue(Task& task) noexcept {
        const size_t prio = task.priority;
        assert(prio < PriorityLevels);

        auto& queue = m_queues[prio];
        task.next = nullptr;
        task.prev = queue.tail;

        if (queue.tail != nullptr) {
            queue.tail->next = &task;
        } else {
            queue.head = &task;
        }
        queue.tail = &task;

        m_active_mask |= (1ULL << prio);
    }

    [[nodiscard]] Task* dequeue_highest() noexcept {
        if (m_active_mask == 0) {
            return nullptr;
        }

        const size_t highest_prio = std::countr_zero(m_active_mask);
        auto& queue = m_queues[highest_prio];
        Task* const task = queue.head;
        assert(task != nullptr);

        queue.head = task->next;
        if (queue.head != nullptr) {
            queue.head->prev = nullptr;
        } else {
            queue.tail = nullptr;
            m_active_mask &= ~(1ULL << highest_prio);
        }

        task->prev = nullptr;
        task->next = nullptr;
        return task;
    }

    [[nodiscard]] bool has_work() const noexcept {
        return m_active_mask != 0;
    }

    [[nodiscard]] size_t active_priority_count() const noexcept {
        return std::popcount(m_active_mask);
    }

private:
    struct PriorityList {
        Task* head{nullptr};
        Task* tail{nullptr};
    };

    uint64_t m_active_mask{0};
    std::array<PriorityList, PriorityLevels> m_queues{};
};
