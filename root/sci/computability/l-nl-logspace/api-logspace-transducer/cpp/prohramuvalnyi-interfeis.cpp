// C++20 Fixed Work-Tape Allocator Specification
#include <cstddef>
#include <cstdint>
#include <span>
#include <array>
#include <expected>
#include <new>

namespace space_complexity {

template <size_t BufferSize = 4096>
class FixedWorkTape {
public:
    constexpr FixedWorkTape() noexcept : offset_(0) {}

    // Non-copyable, non-movable to guarantee physical memory stability
    FixedWorkTape(const FixedWorkTape&) = delete;
    FixedWorkTape& operator=(const FixedWorkTape&) = delete;

    [[nodiscard]] std::expected<std::span<uint8_t>, std::errc> allocate(size_t bytes) noexcept {
        const size_t aligned = (bytes + 7) & ~size_t{7};
        if (offset_ + aligned > BufferSize) {
            return std::unexpected(std::errc::not_enough_memory);
        }
        uint8_t* ptr = &buffer_[offset_];
        offset_ += aligned;
        return std::span<uint8_t>(ptr, bytes);
    }

    constexpr void reset() noexcept {
        offset_ = 0;
    }

    [[nodiscard]] constexpr size_t used_bytes() const noexcept {
        return offset_;
    }

    [[nodiscard]] constexpr size_t capacity() const noexcept {
        return BufferSize;
    }

private:
    alignas(8) std::array<uint8_t, BufferSize> buffer_{};
    size_t offset_{0};
};

} // namespace space_complexity
