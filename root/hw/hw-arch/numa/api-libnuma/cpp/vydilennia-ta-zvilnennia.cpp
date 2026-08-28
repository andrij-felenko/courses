#include <numa.h>
#include <span>
#include <memory>
#include <stdexcept>

template <typename T>
class NumaScopedBlock {
public:
    NumaScopedBlock(std::size_t count, int node) : count_(count), bytes_(count * sizeof(T)) {
        ptr_ = static_cast<T*>(numa_alloc_onnode(bytes_, node));
        if (!ptr_) throw std::bad_alloc();
    }
    ~NumaScopedBlock() noexcept {
        if (ptr_) numa_free(ptr_, bytes_);
    }
    [[nodiscard]] std::span<T> span() noexcept { return {ptr_, count_}; }
private:
    T* ptr_{nullptr};
    std::size_t count_{0};
    std::size_t bytes_{0};
};
