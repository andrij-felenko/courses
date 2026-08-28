#include <iostream>
#include <array>
#include <span>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <algorithm>

template <size_t HeapCapacity = 256 * 1024>
class SegregatedAllocator {
public:
    static constexpr size_t Alignment = 16;
    static constexpr size_t NumBins = 8;
    static constexpr size_t PrevInUseFlag = 0x1;
    static constexpr size_t SizeMask = ~(Alignment - 1);

    enum class AllocError {
        OutOfMemory,
        InvalidSize,
        InvalidPointer
    };

    SegregatedAllocator() noexcept {
        reset();
    }

    void reset() noexcept {
        bins_.fill(nullptr);

        auto* initial = reinterpret_cast<BlockHeader*>(memory_.data());
        initial->prev_size = 0;
        initial->set_size_and_flags(HeapCapacity, true);
        initial->next_free = nullptr;
        initial->prev_free = nullptr;

        bin_insert(initial);
    }

    [[nodiscard]] std::expected<std::span<std::byte>, AllocError> allocate(size_t payload_bytes) noexcept {
        if (payload_bytes == 0 || payload_bytes > HeapCapacity) {
            return std::unexpected(AllocError::InvalidSize);
        }

        const size_t total_size = std::max(align_up(payload_bytes + HeaderOverhead), MinBlockSize);
        const int start_bin = get_bin_index(total_size);
        BlockHeader* victim = nullptr;

        for (size_t i = start_bin; i < NumBins; ++i) {
            BlockHeader* curr = bins_[i];
            while (curr != nullptr) {
                if (curr->get_size() >= total_size) {
                    victim = curr;
                    break;
                }
                curr = curr->next_free;
            }
            if (victim != nullptr) break;
        }

        if (victim == nullptr) {
            return std::unexpected(AllocError::OutOfMemory);
        }

        bin_remove(victim);
        const size_t victim_size = victim->get_size();
        const size_t remainder_size = victim_size - total_size;

        if (remainder_size >= MinBlockSize) {
            victim->set_size_and_flags(total_size, victim->is_prev_inuse());

            auto* remainder = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(victim) + total_size);
            remainder->set_size_and_flags(remainder_size, true);
            remainder->prev_size = total_size;

            if (reinterpret_cast<std::byte*>(remainder) + remainder_size < memory_.data() + HeapCapacity) {
                auto* next_phys = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(remainder) + remainder_size);
                next_phys->prev_size = remainder_size;
            }

            bin_insert(remainder);
        } else {
            if (reinterpret_cast<std::byte*>(victim) + victim_size < memory_.data() + HeapCapacity) {
                auto* next_phys = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(victim) + victim_size);
                next_phys->size_flags |= PrevInUseFlag;
            }
        }

        auto* user_ptr = reinterpret_cast<std::byte*>(victim) + HeaderOverhead;
        return std::span<std::byte>(user_ptr, total_size - HeaderOverhead);
    }

    void deallocate(std::span<std::byte> user_span) noexcept {
        if (user_span.empty() || user_span.data() < memory_.data() ||
            user_span.data() >= memory_.data() + HeapCapacity) {
            return;
        }

        auto* b = reinterpret_cast<BlockHeader*>(user_span.data() - HeaderOverhead);
        size_t size = b->get_size();
        bool prev_inuse = b->is_prev_inuse();

        // Коалесценція назад
        if (!prev_inuse) {
            auto* prev_block = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(b) - b->prev_size);
            bin_remove(prev_block);
            size += prev_block->get_size();
            prev_inuse = prev_block->is_prev_inuse();
            b = prev_block;
        }

        // Коалесценція вперед
        auto* next_block = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(b) + size);
        if (reinterpret_cast<std::byte*>(next_block) < memory_.data() + HeapCapacity) {
            auto* next_next = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(next_block) + next_block->get_size());
            bool next_is_free = true;
            if (reinterpret_cast<std::byte*>(next_next) < memory_.data() + HeapCapacity) {
                next_is_free = !next_next->is_prev_inuse();
            }

            if (next_is_free) {
                bin_remove(next_block);
                size += next_block->get_size();
            } else {
                next_block->size_flags &= ~PrevInUseFlag;
                next_block->prev_size = size;
            }
        }

        b->set_size_and_flags(size, prev_inuse);

        auto* next_phys = reinterpret_cast<BlockHeader*>(reinterpret_cast<std::byte*>(b) + size);
        if (reinterpret_cast<std::byte*>(next_phys) < memory_.data() + HeapCapacity) {
            next_phys->prev_size = size;
            next_phys->size_flags &= ~PrevInUseFlag;
        }

        bin_insert(b);
    }

private:
    struct BlockHeader {
        size_t prev_size{0};
        size_t size_flags{0};
        BlockHeader* next_free{nullptr};
        BlockHeader* prev_free{nullptr};

        [[nodiscard]] size_t get_size() const noexcept {
            return size_flags & SizeMask;
        }

        [[nodiscard]] bool is_prev_inuse() const noexcept {
            return (size_flags & PrevInUseFlag) != 0;
        }

        void set_size_and_flags(size_t sz, bool prev_busy) noexcept {
            size_flags = (sz & SizeMask) | (prev_busy ? PrevInUseFlag : 0);
        }
    };

    static constexpr size_t HeaderOverhead = sizeof(size_t) * 2;
    static constexpr size_t MinBlockSize = (sizeof(BlockHeader) + Alignment - 1) & ~(Alignment - 1);

    alignas(std::max_align_t) std::array<std::byte, HeapCapacity> memory_{};
    std::array<BlockHeader*, NumBins> bins_{};

    [[nodiscard]] static constexpr size_t align_up(size_t sz) noexcept {
        return (sz + (Alignment - 1)) & ~(Alignment - 1);
    }

    [[nodiscard]] static int get_bin_index(size_t sz) noexcept {
        if (sz <= 64)   return 0;
        if (sz <= 128)  return 1;
        if (sz <= 256)  return 2;
        if (sz <= 512)  return 3;
        if (sz <= 1024) return 4;
        if (sz <= 4096) return 5;
        if (sz <= 16384) return 6;
        return 7;
    }

    void bin_insert(BlockHeader* b) noexcept {
        const int idx = get_bin_index(b->get_size());
        b->next_free = bins_[idx];
        b->prev_free = nullptr;
        if (bins_[idx] != nullptr) {
            bins_[idx]->prev_free = b;
        }
        bins_[idx] = b;
    }

    void bin_remove(BlockHeader* b) noexcept {
        const int idx = get_bin_index(b->get_size());
        if (b->prev_free != nullptr) {
            b->prev_free->next_free = b->next_free;
        } else {
            bins_[idx] = b->next_free;
        }
        if (b->next_free != nullptr) {
            b->next_free->prev_free = b->prev_free;
        }
        b->next_free = nullptr;
        b->prev_free = nullptr;
    }
};
