#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <memory>
#include <concepts>
#include <bit>
#include <algorithm>

template <size_t MinOrder = 4, size_t MaxOrder = 16>
class BuddyAllocator {
public:
    static constexpr size_t MinBlockSize = 1ULL << MinOrder;
    static constexpr size_t TotalPoolSize = 1ULL << MaxOrder;
    static constexpr size_t NumOrders = MaxOrder - MinOrder + 1;
    static constexpr size_t NumTags = 1ULL << (MaxOrder - MinOrder);

    struct BlockTag {
        uint8_t order{0};
        bool is_free{false};
    };

    struct ListNode {
        ListNode* prev{nullptr};
        ListNode* next{nullptr};
    };

    explicit BuddyAllocator(std::span<std::byte, TotalPoolSize> buffer) noexcept
        : pool_(buffer.data()) {
        for (auto& head : free_lists_) {
            head.prev = &head;
            head.next = &head;
        }

        // Початковий стан: монолітний блок максимального порядку
        auto* root = reinterpret_cast<ListNode*>(pool_);
        push_node(free_lists_[NumOrders - 1], *root);
        tags_[0] = BlockTag{.order = static_cast<uint8_t>(MaxOrder), .is_free = true};
    }

    // Заборона копіювання, підтримка переміщення
    BuddyAllocator(const BuddyAllocator&) = delete;
    BuddyAllocator& operator=(const BuddyAllocator&) = delete;
    BuddyAllocator(BuddyAllocator&&) noexcept = default;
    BuddyAllocator& operator=(BuddyAllocator&&) noexcept = default;

    [[nodiscard]] std::span<std::byte> allocate(size_t bytes) noexcept {
        if (bytes == 0 || bytes > TotalPoolSize) {
            return {};
        }

        const uint8_t target_order = size_to_order(bytes);
        uint8_t current_order = target_order;

        while (current_order <= MaxOrder) {
            const size_t list_idx = current_order - MinOrder;
            if (!is_list_empty(free_lists_[list_idx])) {
                break;
            }
            ++current_order;
        }

        if (current_order > MaxOrder) {
            return {}; // Недостатньо пам'яті
        }

        ListNode* block = pop_node(free_lists_[current_order - MinOrder]);
        uintptr_t block_offset = reinterpret_cast<std::byte*>(block) - pool_;

        // Розщеплення донорів
        while (current_order > target_order) {
            --current_order;
            const size_t half_size = 1ULL << current_order;
            const uintptr_t buddy_offset = block_offset + half_size;

            auto* buddy = reinterpret_cast<ListNode*>(pool_ + buddy_offset);
            push_node(free_lists_[current_order - MinOrder], *buddy);

            const size_t buddy_tag_idx = buddy_offset >> MinOrder;
            tags_[buddy_tag_idx] = BlockTag{current_order, true};
        }

        const size_t block_tag_idx = block_offset >> MinOrder;
        tags_[block_tag_idx] = BlockTag{target_order, false};

        return {pool_ + block_offset, 1ULL << target_order};
    }

    void deallocate(std::span<std::byte> block) noexcept {
        if (block.empty() || block.data() < pool_ || block.data() >= pool_ + TotalPoolSize) {
            return;
        }

        uintptr_t block_offset = block.data() - pool_;
        size_t tag_idx = block_offset >> MinOrder;
        uint8_t order = tags_[tag_idx].order;

        if (tags_[tag_idx].is_free) {
            return; // Захист від повторного звільнення
        }

        while (order < MaxOrder) {
            const uintptr_t buddy_offset = block_offset ^ (1ULL << order);
            const size_t buddy_tag_idx = buddy_offset >> MinOrder;

            // Перевірка статусу близнюка
            if (!tags_[buddy_tag_idx].is_free || tags_[buddy_tag_idx].order != order) {
                break;
            }

            auto* buddy_node = reinterpret_cast<ListNode*>(pool_ + buddy_offset);
            remove_node(*buddy_node);

            tags_[buddy_tag_idx] = BlockTag{0, false};
            block_offset &= ~(1ULL << order);
            tag_idx = block_offset >> MinOrder;
            ++order;
        }

        auto* final_block = reinterpret_cast<ListNode*>(pool_ + block_offset);
        push_node(free_lists_[order - MinOrder], *final_block);
        tags_[tag_idx] = BlockTag{order, true};
    }

private:
    [[nodiscard]] static uint8_t size_to_order(size_t size) noexcept {
        if (size <= MinBlockSize) return static_cast<uint8_t>(MinOrder);
        return static_cast<uint8_t>(std::max<size_t>(MinOrder, std::bit_width(size - 1)));
    }

    static void push_node(ListNode& head, ListNode& node) noexcept {
        node.next = head.next;
        node.prev = &head;
        head.next->prev = &node;
        head.next = &node;
    }

    static void remove_node(ListNode& node) noexcept {
        node.prev->next = node.next;
        node.next->prev = node.prev;
        node.prev = nullptr;
        node.next = nullptr;
    }

    static ListNode* pop_node(ListNode& head) noexcept {
        if (is_list_empty(head)) return nullptr;
        ListNode* node = head.next;
        remove_node(*node);
        return node;
    }

    [[nodiscard]] static bool is_list_empty(const ListNode& head) noexcept {
        return head.next == &head;
    }

    std::byte* pool_{nullptr};
    std::array<ListNode, NumOrders> free_lists_{};
    std::array<BlockTag, NumTags> tags_{};
};

// Безпечна RAII-обгортка для автоматичного керування життєвим циклом виділеного блока
template <typename AllocatorType>
class BuddyBlock {
public:
    BuddyBlock() noexcept = default;

    BuddyBlock(AllocatorType& alloc, size_t bytes) noexcept
        : alloc_(&alloc), span_(alloc_->allocate(bytes)) {}

    ~BuddyBlock() noexcept {
        reset();
    }

    // Заборона копіювання, підтримка переміщення володіння
    BuddyBlock(const BuddyBlock&) = delete;
    BuddyBlock& operator=(const BuddyBlock&) = delete;

    BuddyBlock(BuddyBlock&& other) noexcept
        : alloc_(other.alloc_), span_(other.span_) {
        other.alloc_ = nullptr;
        other.span_ = {};
    }

    BuddyBlock& operator=(BuddyBlock&& other) noexcept {
        if (this != &other) {
            reset();
            alloc_ = other.alloc_;
            span_ = other.span_;
            other.alloc_ = nullptr;
            other.span_ = {};
        }
        return *this;
    }

    [[nodiscard]] std::span<std::byte> get() const noexcept { return span_; }
    [[nodiscard]] std::byte* data() const noexcept { return span_.data(); }
    [[nodiscard]] size_t size() const noexcept { return span_.size(); }
    [[nodiscard]] bool empty() const noexcept { return span_.empty(); }

    void reset() noexcept {
        if (alloc_ && !span_.empty()) {
            alloc_->deallocate(span_);
            span_ = {};
        }
    }

private:
    AllocatorType* alloc_{nullptr};
    std::span<std::byte> span_{};
};
