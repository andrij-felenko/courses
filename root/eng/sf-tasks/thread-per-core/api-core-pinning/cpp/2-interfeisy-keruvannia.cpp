#include <memory>
#include <new>
#include <numa.h>
#include <numaif.h>

namespace tpc {

/* Шаблонний C++ алокатор пам'яті для конкретного NUMA-вузла */
template <typename T>
struct NumaAllocator {
    using value_type = T;
    int target_node{0};

    explicit NumaAllocator(int node) noexcept : target_node(node) {}

    template <typename U>
    NumaAllocator(const NumaAllocator<U>& other) noexcept : target_node(other.target_node) {}

    T* allocate(std::size_t n) {
        void* ptr = numa_alloc_onnode(n * sizeof(T), target_node);
        if (!ptr) {
            throw std::bad_alloc();
        }
        return static_cast<T*>(ptr);
    }

    void deallocate(T* p, std::size_t n) noexcept {
        numa_free(p, n * sizeof(T));
    }
};

} // namespace tpc
