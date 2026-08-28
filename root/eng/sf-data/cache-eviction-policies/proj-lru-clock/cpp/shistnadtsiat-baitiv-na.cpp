#include <cstddef>
#include <memory>

inline size_t g_index_bytes = 0;              // C++17 inline-змінна

template <class T>
struct CountingAlloc {
    using value_type = T;
    CountingAlloc() = default;
    template <class U> CountingAlloc(const CountingAlloc<U>&) {}

    T* allocate(size_t n) {
        g_index_bytes += n * sizeof(T);
        return std::allocator<T>{}.allocate(n);
    }
    void deallocate(T* p, size_t n) {
        g_index_bytes -= n * sizeof(T);
        std::allocator<T>{}.deallocate(p, n);
    }
    template <class U> bool operator==(const CountingAlloc<U>&) const { return true; }
};

using Index = std::unordered_map<
    uint64_t, uint32_t, std::hash<uint64_t>, std::equal_to<uint64_t>,
    CountingAlloc<std::pair<const uint64_t, uint32_t>>>;

// заповнити Index десятьма мільйонами пар і надрукувати g_index_bytes / 10'000'000
