#include <memory_resource>

class TrackingMemoryResource : public std::pmr::memory_resource {
public:
    explicit TrackingMemoryResource(std::pmr::memory_resource* upstream = std::pmr::get_default_resource())
        : upstream_(upstream) {}

protected:
    void* do_allocate(std::size_t bytes, std::size_t alignment) override {
        void* ptr = upstream_->allocate(bytes, alignment);
        active_bytes_.fetch_add(bytes, std::memory_order_relaxed);
        return ptr;
    }

    void do_deallocate(void* ptr, std::size_t bytes, std::size_t alignment) override {
        active_bytes_.fetch_sub(bytes, std::memory_order_relaxed);
        upstream_->deallocate(ptr, bytes, alignment);
    }

    bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override {
        return this == &other;
    }

private:
    std::pmr::memory_resource* upstream_;
    std::atomic<std::size_t> active_bytes_{0};
};
