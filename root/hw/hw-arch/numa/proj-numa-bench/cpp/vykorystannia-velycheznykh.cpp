#include <sys/mman.h>
#include <numaif.h>
#include <cstddef>
#include <stdexcept>
#include <format>
#include <span>

class NumaHugePageBuffer {
public:
    NumaHugePageBuffer(std::size_t bytes, int node) : bytes_(bytes), node_(node) {
        // Розмір має бути кратним 2 МБ
        constexpr std::size_t huge_page_size = 2 * 1024 * 1024;
        if (bytes_ % huge_page_size != 0) {
            bytes_ = ((bytes_ + huge_page_size - 1) / huge_page_size) * huge_page_size;
        }

        void* ptr = mmap(nullptr, bytes_,
                         PROT_READ | PROT_WRITE,
                         MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                         -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::runtime_error("mmap MAP_HUGETLB failed: перевірте наявність вільних HugePages");
        }

        unsigned long nodemask = (1UL << node_);
        if (mbind(ptr, bytes_, MPOL_BIND, &nodemask, sizeof(nodemask) * 8, MPOL_MF_MOVE) != 0) {
            munmap(ptr, bytes_);
            throw std::runtime_error(std::format("mbind failed для вузла {}", node_));
        }

        data_ = static_cast<std::byte*>(ptr);
    }

    ~NumaHugePageBuffer() noexcept {
        if (data_) munmap(data_, bytes_);
    }

    NumaHugePageBuffer(const NumaHugePageBuffer&) = delete;
    NumaHugePageBuffer& operator=(const NumaHugePageBuffer&) = delete;

    [[nodiscard]] std::span<std::byte> span() noexcept { return {data_, bytes_}; }
    [[nodiscard]] std::size_t size_bytes() const noexcept { return bytes_; }
    [[nodiscard]] int node() const noexcept { return node_; }

private:
    std::byte* data_{nullptr};
    std::size_t bytes_{0};
    int node_{0};
};
