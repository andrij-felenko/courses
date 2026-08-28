// Фіксовані блоки пам'яті для телеметрії без malloc() (RAII-обгортка).
// Обґрунтування та аналіз відкинутих варіантів: doc/adr/0005-static-can-pools.md
//
// Контекст: купа фрагментується на пікових навантаженнях CAN-шини.
// RAII-дескриптор гарантує вивільнення блоку в пулі при виході зі скоупу.

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <bit>

struct alignas(4) PacketBlock {
    std::array<std::uint8_t, 64> payload{};
    std::uint16_t length{0};
    std::uint32_t timestamp_us{0};
};

template <std::size_t Capacity = 32>
requires (Capacity <= 32)
class StaticPacketPool {
public:
    class ScopedHandle {
    public:
        ScopedHandle(StaticPacketPool& pool, std::size_t index) noexcept
            : pool_(&pool), index_(index) {}

        ~ScopedHandle() noexcept {
            if (pool_ != nullptr) {
                pool_->release(index_);
            }
        }

        ScopedHandle(const ScopedHandle&) = delete;
        ScopedHandle& operator=(const ScopedHandle&) = delete;

        ScopedHandle(ScopedHandle&& other) noexcept
            : pool_(other.pool_), index_(other.index_) {
            other.pool_ = nullptr;
        }

        ScopedHandle& operator=(ScopedHandle&& other) noexcept {
            if (this != &other) {
                if (pool_ != nullptr) {
                    pool_->release(index_);
                }
                pool_ = other.pool_;
                index_ = other.index_;
                other.pool_ = nullptr;
            }
            return *this;
        }

        [[nodiscard]] PacketBlock& get() noexcept {
            return pool_->blocks_[index_];
        }

        [[nodiscard]] const PacketBlock& get() const noexcept {
            return pool_->blocks_[index_];
        }

    private:
        StaticPacketPool* pool_{nullptr};
        std::size_t index_{0};
    };

    [[nodiscard]] std::optional<ScopedHandle> acquire() noexcept {
        if (allocated_mask_ == 0xFFFF'FFFFU) {
            return std::nullopt; // Пул вичерпано
        }

        const auto free_index = static_cast<std::size_t>(std::countr_one(allocated_mask_));
        if (free_index >= Capacity) {
            return std::nullopt;
        }

        allocated_mask_ |= (1UL << free_index);
        return ScopedHandle(*this, free_index);
    }

private:
    friend class ScopedHandle;

    void release(std::size_t index) noexcept {
        if (index < Capacity) {
            allocated_mask_ &= ~(1UL << index);
        }
    }

    std::array<PacketBlock, Capacity> blocks_{};
    std::uint32_t allocated_mask_{0};
};
