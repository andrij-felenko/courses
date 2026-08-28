#include <cstddef>
#include <cstdint>
#include <new>
#include <utility>
#include <memory>
#include <vector>
#include <iostream>

class Arena {
public:
    explicit Arena(std::size_t capacity)
        : capacity_(capacity),
          buffer_(static_cast<std::byte*>(::operator new(capacity, std::align_val_t{alignof(std::max_align_t)}))),
          offset_(0) {}

    ~Arena() {
        ::operator delete(buffer_, std::align_val_t{alignof(std::max_align_t)});
    }

    Arena(const Arena&) = delete;
    Arena& operator=(const Arena&) = delete;

    Arena(Arena&& other) noexcept
        : capacity_(other.capacity_),
          buffer_(other.buffer_),
          offset_(other.offset_) {
        other.buffer_ = nullptr;
        other.capacity_ = 0;
        other.offset_ = 0;
    }

    Arena& operator=(Arena&& other) noexcept {
        if (this != &other) {
            ::operator delete(buffer_, std::align_val_t{alignof(std::max_align_t)});
            capacity_ = other.capacity_;
            buffer_ = other.buffer_;
            offset_ = other.offset_;
            other.buffer_ = nullptr;
            other.capacity_ = 0;
            other.offset_ = 0;
        }
        return *this;
    }

    [[nodiscard]] void* allocate(std::size_t bytes, std::size_t alignment) {
        std::size_t aligned_offset = (offset_ + alignment - 1) & ~(alignment - 1);

        if (aligned_offset + bytes > capacity_) {
            throw std::bad_alloc();
        }

        offset_ = aligned_offset + bytes;
        return buffer_ + aligned_offset;
    }

    void deallocate(void* /*p*/, std::size_t /*bytes*/) noexcept {
        // Лінійна арена не підтримує поштучне звільнення
    }

    void reset() noexcept {
        offset_ = 0;
    }

    [[nodiscard]] std::size_t used_bytes() const noexcept { return offset_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }

private:
    std::size_t capacity_;
    std::byte* buffer_;
    std::size_t offset_;
};
