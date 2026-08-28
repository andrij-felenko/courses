namespace std::pmr {

template <class T = std::byte>
class polymorphic_allocator {
public:
    using value_type = T;

    polymorphic_allocator() noexcept : res_(get_default_resource()) {}
    polymorphic_allocator(memory_resource* r) noexcept : res_(r ? r : get_default_resource()) {}
    polymorphic_allocator(const polymorphic_allocator& other) = default;

    template <class U>
    polymorphic_allocator(const polymorphic_allocator<U>& other) noexcept : res_(other.resource()) {}

    [[nodiscard]] T* allocate(std::size_t n) {
        return static_cast<T*>(res_->allocate(n * sizeof(T), alignof(T)));
    }

    void deallocate(T* p, std::size_t n) noexcept {
        res_->deallocate(p, n * sizeof(T), alignof(T));
    }

    [[nodiscard]] void* allocate_bytes(std::size_t nbytes, std::size_t alignment = alignof(std::max_align_t)) {
        return res_->allocate(nbytes, alignment);
    }

    void deallocate_bytes(void* p, std::size_t nbytes, std::size_t alignment = alignof(std::max_align_t)) noexcept {
        res_->deallocate(p, nbytes, alignment);
    }

    template <class U, class... Args>
    void construct(U* p, Args&&... args);

    template <class U>
    void destroy(U* p) noexcept {
        p->~U();
    }

    memory_resource* resource() const noexcept { return res_; }

    polymorphic_allocator select_on_container_copy_construction() const noexcept {
        return polymorphic_allocator();
    }

private:
    memory_resource* res_;
};

template <class T1, class T2>
bool operator==(const polymorphic_allocator<T1>& a, const polymorphic_allocator<T2>& b) noexcept {
    return *a.resource() == *b.resource();
}

} // namespace std::pmr
