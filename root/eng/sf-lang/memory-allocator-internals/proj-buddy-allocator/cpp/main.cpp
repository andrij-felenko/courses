#include <iostream>
#include <array>
#include <span>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <algorithm>

template <size_t MinOrder = 10, size_t MaxOrder = 16>
class BuddyAllocator {
public:
    static constexpr size_t MinBlockSize = 1ULL << MinOrder;
    static constexpr size_t PoolSize = 1ULL << MaxOrder;
    static constexpr size_t NumOrders = MaxOrder - MinOrder + 1;
    static constexpr size_t TotalMinBlocks = PoolSize / MinBlockSize;

    enum class Error {
        OutOfMemory,
        InvalidSize,
        InvalidPointer
    };

    BuddyAllocator() noexcept {
        reset();
    }

    void reset() noexcept {
        free_lists_.fill(nullptr);
        is_free_.fill(false);

        auto* initial_block = reinterpret_cast<BlockNode*>(memory_pool_.data());
        initial_block->next = nullptr;
        free_lists_[NumOrders - 1] = initial_block;
        is_free_[0] = true;
    }

    [[nodiscard]] std::expected<std::span<std::byte>, Error> allocate(size_t size) noexcept {
        if (size == 0 || size > PoolSize) {
            return std::unexpected(Error::InvalidSize);
        }

        const size_t req_order = size_to_order(size);
        size_t current_order = req_order;

        while (current_order < NumOrders && free_lists_[current_order] == nullptr) {
            ++current_order;
        }

        if (current_order == NumOrders) {
            return std::unexpected(Error::OutOfMemory);
        }

        BlockNode* block = free_lists_[current_order];
        free_lists_[current_order] = block->next;

        while (current_order > req_order) {
            --current_order;
            const size_t half_size = order_to_size(current_order);
            auto* buddy = reinterpret_cast<BlockNode*>(reinterpret_cast<std::byte*>(block) + half_size);

            buddy->next = free_lists_[current_order];
            free_lists_[current_order] = buddy;

            const size_t buddy_idx = (reinterpret_cast<std::byte*>(buddy) - memory_pool_.data()) >> MinOrder;
            is_free_[buddy_idx] = true;
        }

        const size_t block_idx = (reinterpret_cast<std::byte*>(block) - memory_pool_.data()) >> MinOrder;
        is_free_[block_idx] = false;

        const size_t allocated_size = order_to_size(req_order);
        return std::span<std::byte>(reinterpret_cast<std::byte*>(block), allocated_size);
    }

    void deallocate(std::span<std::byte> block_span) noexcept {
        if (block_span.empty() || block_span.data() < memory_pool_.data() ||
            block_span.data() >= memory_pool_.data() + PoolSize) {
            return;
        }

        size_t order = size_to_order(block_span.size());
        auto* block_addr = block_span.data();

        while (order < NumOrders - 1) {
            const size_t block_size = order_to_size(order);
            const size_t block_offset = block_addr - memory_pool_.data();
            const size_t buddy_offset = block_offset ^ block_size;
            auto* buddy_addr = memory_pool_.data() + buddy_offset;

            const size_t buddy_idx = buddy_offset >> MinOrder;
            if (!is_free_[buddy_idx]) {
                break;
            }

            list_remove(order, reinterpret_cast<BlockNode*>(buddy_addr));
            is_free_[buddy_idx] = false;

            if (buddy_addr < block_addr) {
                block_addr = buddy_addr;
            }

            ++order;
        }

        auto* free_block = reinterpret_cast<BlockNode*>(block_addr);
        free_block->next = free_lists_[order];
        free_lists_[order] = free_block;

        const size_t final_idx = (block_addr - memory_pool_.data()) >> MinOrder;
        is_free_[final_idx] = true;
    }

private:
    struct BlockNode {
        BlockNode* next{nullptr};
    };

    alignas(std::max_align_t) std::array<std::byte, PoolSize> memory_pool_{};
    std::array<BlockNode*, NumOrders> free_lists_{};
    std::array<bool, TotalMinBlocks> is_free_{};

    [[nodiscard]] static constexpr size_t order_to_size(size_t order_idx) noexcept {
        return 1ULL << (MinOrder + order_idx);
    }

    [[nodiscard]] static constexpr size_t size_to_order(size_t size) noexcept {
        size_t actual_size = 1ULL << MinOrder;
        size_t order = 0;
        while (actual_size < size && order < NumOrders - 1) {
            actual_size <<= 1;
            ++order;
        }
        return order;
    }

    void list_remove(size_t order_idx, BlockNode* target) noexcept {
        BlockNode** curr = &free_lists_[order_idx];
        while (*curr != nullptr) {
            if (*curr == target) {
                *curr = target->next;
                return;
            }
            curr = &((*curr)->next);
        }
    }
};
