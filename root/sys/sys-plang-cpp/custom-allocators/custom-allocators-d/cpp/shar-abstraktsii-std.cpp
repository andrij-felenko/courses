template <typename T>
struct SimpleHeapAllocator {
    using value_type = T;

    SimpleHeapAllocator() noexcept = default;
    template <typename U>
    SimpleHeapAllocator(const SimpleHeapAllocator<U>&) noexcept {}

    [[nodiscard]] T* allocate(std::size_t n) {
        if (n > std::numeric_limits<std::size_t>::max() / sizeof(T)) {
            throw std::bad_alloc();
        }
        void* ptr = ::operator new(n * sizeof(T));
        return static_cast<T*>(ptr);
    }

    void deallocate(T* p, std::size_t /*n*/) noexcept {
        ::operator delete(p);
    }
};
