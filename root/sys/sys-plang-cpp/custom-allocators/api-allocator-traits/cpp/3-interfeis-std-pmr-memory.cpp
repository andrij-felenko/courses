namespace std::pmr {

class memory_resource {
public:
    virtual ~memory_resource() = default;

    // Публічний невіртуальний інтерфейс
    [[nodiscard]] void* allocate(std::size_t bytes, std::size_t alignment = alignof(std::max_align_t)) {
        return do_allocate(bytes, alignment);
    }

    void deallocate(void* p, std::size_t bytes, std::size_t alignment = alignof(std::max_align_t)) {
        do_deallocate(p, bytes, alignment);
    }

    bool is_equal(const memory_resource& other) const noexcept {
        return do_is_equal(other);
    }

protected:
    // Чисті віртуальні методи, які зобов'язана реалізувати конкретна стратегія пам'яті
    virtual void* do_allocate(std::size_t bytes, std::size_t alignment) = 0;
    virtual void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) = 0;
    virtual bool do_is_equal(const memory_resource& other) const noexcept = 0;
};

// Оператори рівності
inline bool operator==(const memory_resource& a, const memory_resource& b) noexcept {
    return &a == &b || a.is_equal(b);
}

inline bool operator!=(const memory_resource& a, const memory_resource& b) noexcept {
    return !(a == b);
}

} // namespace std::pmr
