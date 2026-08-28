#include <array>
#include <cstdint>
#include <functional>
#include <concepts>
#include <memory>
#include <bit>

namespace timing {

constexpr size_t L0_BITS = 8;
constexpr size_t L0_SIZE = 1U << L0_BITS;
constexpr size_t L0_MASK = L0_SIZE - 1;

constexpr size_t LVL_BITS = 6;
constexpr size_t LVL_SIZE = 1U << LVL_BITS;
constexpr size_t LVL_MASK = LVL_SIZE - 1;

class TimerWheel {
public:
    struct TimerNode {
        uint64_t expires_tick{0};
        std::function<void()> callback;
        TimerNode* next{nullptr};
        TimerNode* prev{nullptr};
        int wheel{-1};
        int slot{-1};
        bool active{false};
    };

    explicit TimerWheel(uint64_t start_tick = 0) : current_tick_(start_tick) {
        l0_mask_.fill(0);
    }

    void add(TimerNode* node, uint64_t expires, std::function<void()> cb) {
        node->expires_tick = expires;
        node->callback = std::move(cb);
        node->active = true;

        if (expires <= current_tick_) {
            int slot = static_cast<int>(current_tick_ & L0_MASK);
            list_push(l0_[slot], node);
            l0_mask_[slot / 64] |= (1ULL << (slot % 64));
            node->wheel = 0; node->slot = slot;
            return;
        }

        uint64_t delta = expires - current_tick_;
        if (delta < (1ULL << 8)) {
            int slot = static_cast<int>(expires & L0_MASK);
            list_push(l0_[slot], node);
            l0_mask_[slot / 64] |= (1ULL << (slot % 64));
            node->wheel = 0; node->slot = slot;
        } else if (delta < (1ULL << 14)) {
            int slot = static_cast<int>((expires >> 8) & LVL_MASK);
            list_push(l1_[slot], node);
            l1_mask_ |= (1ULL << slot);
            node->wheel = 1; node->slot = slot;
        } else if (delta < (1ULL << 20)) {
            int slot = static_cast<int>((expires >> 14) & LVL_MASK);
            list_push(l2_[slot], node);
            l2_mask_ |= (1ULL << slot);
            node->wheel = 2; node->slot = slot;
        } else {
            int slot = static_cast<int>((expires >> 20) & LVL_MASK);
            list_push(l3_[slot], node);
            l3_mask_ |= (1ULL << slot);
            node->wheel = 3; node->slot = slot;
        }
    }

    void cancel(TimerNode* node) {
        if (!node->active) return;
        if (node->wheel == 0) {
            list_del(l0_[node->slot], node);
            if (!l0_[node->slot]) l0_mask_[node->slot / 64] &= ~(1ULL << (node->slot % 64));
        } else if (node->wheel == 1) {
            list_del(l1_[node->slot], node);
            if (!l1_[node->slot]) l1_mask_ &= ~(1ULL << node->slot);
        } else if (node->wheel == 2) {
            list_del(l2_[node->slot], node);
            if (!l2_[node->slot]) l2_mask_ &= ~(1ULL << node->slot);
        } else if (node->wheel == 3) {
            list_del(l3_[node->slot], node);
            if (!l3_[node->slot]) l3_mask_ &= ~(1ULL << node->slot);
        }
        node->active = false;
    }

private:
    static void list_push(TimerNode*& head, TimerNode* node) noexcept {
        node->next = head;
        node->prev = nullptr;
        if (head) head->prev = node;
        head = node;
    }

    static void list_del(TimerNode*& head, TimerNode* node) noexcept {
        if (node->prev) node->prev->next = node->next;
        else head = node->next;
        if (node->next) node->next->prev = node->prev;
        node->next = node->prev = nullptr;
    }

    uint64_t current_tick_{0};
    std::array<TimerNode*, L0_SIZE> l0_{};
    std::array<TimerNode*, LVL_SIZE> l1_{};
    std::array<TimerNode*, LVL_SIZE> l2_{};
    std::array<TimerNode*, LVL_SIZE> l3_{};
    std::array<uint64_t, L0_SIZE / 64> l0_mask_{};
    uint64_t l1_mask_{0};
    uint64_t l2_mask_{0};
    uint64_t l3_mask_{0};
};

} // namespace timing
