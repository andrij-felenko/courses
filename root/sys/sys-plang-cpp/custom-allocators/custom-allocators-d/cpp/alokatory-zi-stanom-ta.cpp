template <typename T>
class StatefulArenaAllocator {
public:
    using value_type = T;

    explicit StatefulArenaAllocator(Arena& arena) noexcept : arena_(&arena) {}

    template <typename U>
    StatefulArenaAllocator(const StatefulArenaAllocator<U>& other) noexcept : arena_(other.arena_) {}

    T* allocate(std::size_t n) {
        return static_cast<T*>(arena_->allocate(n * sizeof(T), alignof(T)));
    }

    void deallocate(T* p, std::size_t n) noexcept {
        arena_->deallocate(p, n * sizeof(T));
    }

    bool operator==(const StatefulArenaAllocator& other) const noexcept {
        return arena_ == other.arena_;
    }
    bool operator!=(const StatefulArenaAllocator& other) const noexcept {
        return arena_ != other.arena_;
    }

private:
    Arena* arena_;
    template <typename U> friend class StatefulArenaAllocator;
};
