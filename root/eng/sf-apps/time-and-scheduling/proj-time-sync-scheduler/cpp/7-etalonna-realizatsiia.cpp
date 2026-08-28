#include <iostream>
#include <vector>
#include <array>
#include <cstdint>
#include <chrono>
#include <concepts>
#include <functional>
#include <memory>
#include <bit>
#include <algorithm>

namespace timing {

using Clock = std::chrono::steady_clock;
using Nanoseconds = std::chrono::nanoseconds;
using Milliseconds = std::chrono::milliseconds;

constexpr size_t WHEEL_L0_BITS = 8;
constexpr size_t WHEEL_L0_SIZE = 1U << WHEEL_L0_BITS;
constexpr size_t WHEEL_L0_MASK = WHEEL_L0_SIZE - 1;

constexpr size_t WHEEL_LVL_BITS = 6;
constexpr size_t WHEEL_LVL_SIZE = 1U << WHEEL_LVL_BITS;
constexpr size_t WHEEL_LVL_MASK = WHEEL_LVL_SIZE - 1;

constexpr size_t L0_SHIFT = 0;
constexpr size_t L1_SHIFT = WHEEL_L0_BITS;
constexpr size_t L2_SHIFT = WHEEL_L0_BITS + WHEEL_LVL_BITS;
constexpr size_t L3_SHIFT = WHEEL_L0_BITS + 2 * WHEEL_LVL_BITS;

template <typename Callback>
concept TimerCallback = std::invocable<Callback>;

class HierarchicalTimerWheel {
public:
    struct TimerHandle;

private:
    struct Node {
        uint64_t expires_tick{0};
        uint64_t interval_ticks{0};
        std::function<void()> callback;
        Node* next{nullptr};
        Node* prev{nullptr};
        int current_wheel{-1};
        int current_slot{-1};
        bool is_active{false};
        uint64_t id{0};
    };

    struct Slot {
        Node* head{nullptr};
    };

public:
    struct TimerHandle {
        uint64_t id{0};
        Node* node_ptr{nullptr};

        [[nodiscard]] bool is_valid() const noexcept {
            return node_ptr != nullptr && node_ptr->is_active && node_ptr->id == id;
        }
    };

    explicit HierarchicalTimerWheel(Clock::time_point start_time = Clock::now())
        : base_time_(start_time), current_tick_(0), next_id_(1) {
        l0_mask_.fill(0);
    }

    ~HierarchicalTimerWheel() {
        clear_all();
    }

    HierarchicalTimerWheel(const HierarchicalTimerWheel&) = delete;
    HierarchicalTimerWheel& operator=(const HierarchicalTimerWheel&) = delete;
    HierarchicalTimerWheel(HierarchicalTimerWheel&&) noexcept = default;
    HierarchicalTimerWheel& operator=(HierarchicalTimerWheel&&) noexcept = default;

    template <TimerCallback Fn>
    TimerHandle schedule(Milliseconds delay, Milliseconds interval, Fn&& fn) {
        auto node = std::make_unique<Node>();
        node->expires_tick = current_tick_ + delay.count();
        node->interval_ticks = interval.count();
        node->callback = std::forward<Fn>(fn);
        node->id = next_id_++;

        Node* raw_ptr = node.get();
        nodes_storage_.push_back(std::move(node));

        internal_add_timer(raw_ptr);
        return TimerHandle{.id = raw_ptr->id, .node_ptr = raw_ptr};
    }

    template <TimerCallback Fn>
    TimerHandle schedule_once(Milliseconds delay, Fn&& fn) {
        return schedule(delay, Milliseconds{0}, std::forward<Fn>(fn));
    }

    bool cancel(TimerHandle handle) {
        if (!handle.is_valid()) return false;
        Node* node = handle.node_ptr;
        remove_from_current_slot(node);
        node->is_active = false;
        node->current_wheel = -1;
        node->current_slot = -1;
        return true;
    }

    void advance_to(uint64_t target_tick) {
        while (current_tick_ < target_tick) {
            uint64_t tick = current_tick_;
            int l0_slot = static_cast<int>(tick & WHEEL_L0_MASK);

            if (l0_slot == 0 && tick > 0) {
                int l1_slot = static_cast<int>((tick >> L1_SHIFT) & WHEEL_LVL_MASK);
                cascade_wheel(1, l1_slot);

                if (l1_slot == 0) {
                    int l2_slot = static_cast<int>((tick >> L2_SHIFT) & WHEEL_LVL_MASK);
                    cascade_wheel(2, l2_slot);

                    if (l2_slot == 0) {
                        int l3_slot = static_cast<int>((tick >> L3_SHIFT) & WHEEL_LVL_MASK);
                        cascade_wheel(3, l3_slot);
                    }
                }
            }

            Node* expired_list = l0_[l0_slot].head;
            l0_[l0_slot].head = nullptr;
            clear_bit_l0(l0_slot);

            Node* curr = expired_list;
            while (curr != nullptr) {
                Node* next = curr->next;
                curr->is_active = false;
                curr->current_wheel = -1;
                curr->current_slot = -1;
                curr->next = nullptr;
                curr->prev = nullptr;

                if (curr->callback) {
                    curr->callback();
                }

                if (curr->interval_ticks > 0) {
                    curr->expires_tick = tick + curr->interval_ticks;
                    internal_add_timer(curr);
                }

                curr = next;
            }

            current_tick_++;
        }
    }

    void poll() {
        auto now = Clock::now();
        auto elapsed = std::chrono::duration_cast<Milliseconds>(now - base_time_).count();
        if (elapsed > static_cast<int64_t>(current_tick_)) {
            advance_to(static_cast<uint64_t>(elapsed));
        }
    }

    [[nodiscard]] uint64_t current_tick() const noexcept {
        return current_tick_;
    }

private:
    static void list_insert(Slot& slot, Node* node) noexcept {
        node->next = slot.head;
        node->prev = nullptr;
        if (slot.head != nullptr) {
            slot.head->prev = node;
        }
        slot.head = node;
    }

    static void list_remove(Slot& slot, Node* node) noexcept {
        if (node->prev != nullptr) {
            node->prev->next = node->next;
        } else {
            slot.head = node->next;
        }
        if (node->next != nullptr) {
            node->next->prev = node->prev;
        }
        node->next = nullptr;
        node->prev = nullptr;
    }

    void set_bit_l0(int slot) {
        l0_mask_[slot / 64] |= (1ULL << (slot % 64));
    }

    void clear_bit_l0(int slot) {
        l0_mask_[slot / 64] &= ~(1ULL << (slot % 64));
    }

    void internal_add_timer(Node* node) {
        const uint64_t expires = node->expires_tick;
        const uint64_t current = current_tick_;

        if (expires <= current) {
            int slot = static_cast<int>(current & WHEEL_L0_MASK);
            list_insert(l0_[slot], node);
            set_bit_l0(slot);
            node->current_wheel = 0;
            node->current_slot = slot;
            node->is_active = true;
            return;
        }

        const uint64_t delta = expires - current;

        if (delta < (1ULL << L1_SHIFT)) {
            int slot = static_cast<int>(expires & WHEEL_L0_MASK);
            list_insert(l0_[slot], node);
            set_bit_l0(slot);
            node->current_wheel = 0;
            node->current_slot = slot;
        } else if (delta < (1ULL << L2_SHIFT)) {
            int slot = static_cast<int>((expires >> L1_SHIFT) & WHEEL_LVL_MASK);
            list_insert(l1_[slot], node);
            l1_mask_ |= (1ULL << slot);
            node->current_wheel = 1;
            node->current_slot = slot;
        } else if (delta < (1ULL << L3_SHIFT)) {
            int slot = static_cast<int>((expires >> L2_SHIFT) & WHEEL_LVL_MASK);
            list_insert(l2_[slot], node);
            l2_mask_ |= (1ULL << slot);
            node->current_wheel = 2;
            node->current_slot = slot;
        } else {
            int slot = static_cast<int>((expires >> L3_SHIFT) & WHEEL_LVL_MASK);
            list_insert(l3_[slot], node);
            l3_mask_ |= (1ULL << slot);
            node->current_wheel = 3;
            node->current_slot = slot;
        }
        node->is_active = true;
    }

    void remove_from_current_slot(Node* node) {
        if (node->current_wheel == 0) {
            list_remove(l0_[node->current_slot], node);
            if (l0_[node->current_slot].head == nullptr) {
                clear_bit_l0(node->current_slot);
            }
        } else if (node->current_wheel == 1) {
            list_remove(l1_[node->current_slot], node);
            if (l1_[node->current_slot].head == nullptr) {
                l1_mask_ &= ~(1ULL << node->current_slot);
            }
        } else if (node->current_wheel == 2) {
            list_remove(l2_[node->current_slot], node);
            if (l2_[node->current_slot].head == nullptr) {
                l2_mask_ &= ~(1ULL << node->current_slot);
            }
        } else if (node->current_wheel == 3) {
            list_remove(l3_[node->current_slot], node);
            if (l3_[node->current_slot].head == nullptr) {
                l3_mask_ &= ~(1ULL << node->current_slot);
            }
        }
    }

    void cascade_wheel(int wheel_idx, int slot_idx) {
        Slot* slot = nullptr;
        if (wheel_idx == 1) {
            slot = &l1_[slot_idx];
            l1_mask_ &= ~(1ULL << slot_idx);
        } else if (wheel_idx == 2) {
            slot = &l2_[slot_idx];
            l2_mask_ &= ~(1ULL << slot_idx);
        } else if (wheel_idx == 3) {
            slot = &l3_[slot_idx];
            l3_mask_ &= ~(1ULL << slot_idx);
        }

        if (slot == nullptr || slot->head == nullptr) return;

        Node* curr = slot->head;
        slot->head = nullptr;

        while (curr != nullptr) {
            Node* next = curr->next;
            curr->next = nullptr;
            curr->prev = nullptr;
            curr->is_active = false;
            curr->current_wheel = -1;
            curr->current_slot = -1;

            internal_add_timer(curr);
            curr = next;
        }
    }

    void clear_all() {
        for (auto& s : l0_) s.head = nullptr;
        for (auto& s : l1_) s.head = nullptr;
        for (auto& s : l2_) s.head = nullptr;
        for (auto& s : l3_) s.head = nullptr;
        l0_mask_.fill(0);
        l1_mask_ = 0;
        l2_mask_ = 0;
        l3_mask_ = 0;
        nodes_storage_.clear();
    }

    Clock::time_point base_time_;
    uint64_t current_tick_{0};
    uint64_t next_id_{1};

    std::array<Slot, WHEEL_L0_SIZE> l0_{};
    std::array<Slot, WHEEL_LVL_SIZE> l1_{};
    std::array<Slot, WHEEL_LVL_SIZE> l2_{};
    std::array<Slot, WHEEL_LVL_SIZE> l3_{};

    std::array<uint64_t, WHEEL_L0_SIZE / 64> l0_mask_{};
    uint64_t l1_mask_{0};
    uint64_t l2_mask_{0};
    uint64_t l3_mask_{0};

    std::vector<std::unique_ptr<Node>> nodes_storage_;
};

} // namespace timing
