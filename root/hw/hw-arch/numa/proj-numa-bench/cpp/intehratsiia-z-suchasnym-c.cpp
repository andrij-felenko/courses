#include <memory_resource>
#include <numa.h>
#include <format>
#include <stdexcept>

class NumaMemoryResource : public std::pmr::memory_resource {
public:
    explicit NumaMemoryResource(int node) : node_(node) {
        if (numa_available() < 0) {
            throw std::runtime_error("NUMA не підтримується системою");
        }
    }

    [[nodiscard]] int node() const noexcept { return node_; }

protected:
    void* do_allocate(std::size_t bytes, std::size_t alignment) override {
        // libnuma виділяє пам'ять сторінками, тому вирівнювання задовольняється автоматично
        void* ptr = numa_alloc_onnode(bytes, node_);
        if (!ptr) {
            throw std::bad_alloc();
        }
        return ptr;
    }

    void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) override {
        numa_free(p, bytes);
    }

    bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override {
        if (this == &other) return true;
        const auto* casted = dynamic_cast<const NumaMemoryResource*>(&other);
        return casted && (casted->node_ == node_);
    }

private:
    int node_{0};
};
