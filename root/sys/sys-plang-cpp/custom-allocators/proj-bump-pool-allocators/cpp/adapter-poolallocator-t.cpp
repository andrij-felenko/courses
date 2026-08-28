template <typename T>
class PoolAllocator {
public:
    using value_type = T;

    explicit PoolAllocator(FixedPool& pool) noexcept : pool_(&pool) {}

    template <typename U>
    PoolAllocator(const PoolAllocator<U>& other) noexcept : pool_(other.pool_) {}

    [[nodiscard]] T* allocate(std::size_t n) {
        if (n != 1) {
            throw std::bad_alloc();
        }
        return static_cast<T*>(pool_->allocate());
    }

    void deallocate(T* p, std::size_t n) noexcept {
        if (n == 1) {
            pool_->deallocate(p);
        }
    }

    template <typename U>
    bool operator==(const PoolAllocator<U>& other) const noexcept {
        return pool_ == other.pool_;
    }

    template <typename U>
    bool operator!=(const PoolAllocator<U>& other) const noexcept {
        return !(*this == other);
    }

    template <typename U>
    friend class PoolAllocator;

private:
    FixedPool* pool_;
};
