#include <memory_resource>

template <std::size_t BufferSize>
class StackBufferResource : public std::pmr::memory_resource {
public:
    explicit StackBufferResource(std::pmr::memory_resource* upstream = std::pmr::get_default_resource())
        : upstream_(upstream), offset_(0) {}

    ~StackBufferResource() override = default;

    [[nodiscard]] std::size_t bytes_used_on_stack() const noexcept { return offset_; }
    [[nodiscard]] std::size_t upstream_alloc_count() const noexcept { return upstream_count_; }

protected:
    void* do_allocate(std::size_t bytes, std::size_t alignment) override {
        std::size_t aligned_offset = (offset_ + alignment - 1) & ~(alignment - 1);

        if (aligned_offset + bytes <= BufferSize) {
            offset_ = aligned_offset + bytes;
            return stack_buffer_ + aligned_offset;
        }

        upstream_count_++;
        return upstream_->allocate(bytes, alignment);
    }

    void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) override {
        if (p >= stack_buffer_ && p < stack_buffer_ + BufferSize) {
            return;
        }
        upstream_->deallocate(p, bytes, alignment);
    }

    bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override {
        return this == &other;
    }

private:
    alignas(std::max_align_t) std::byte stack_buffer_[BufferSize];
    std::pmr::memory_resource* upstream_;
    std::size_t offset_;
    std::size_t upstream_count_ = 0;
};
