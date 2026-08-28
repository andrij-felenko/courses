#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <span>
#include <sys/mman.h>
#include <unistd.h>
#include <system_error>

class MmapRegion {
public:
    explicit MmapRegion(size_t size) : size_(size) {
        void* ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
        addr_ = static_cast<std::byte*>(ptr);
    }

    ~MmapRegion() noexcept {
        if (addr_ != nullptr) {
            ::munmap(addr_, size_);
        }
    }

    MmapRegion(const MmapRegion&) = delete;
    MmapRegion& operator=(const MmapRegion&) = delete;
    MmapRegion(MmapRegion&& other) noexcept : addr_(other.addr_), size_(other.size_) {
        other.addr_ = nullptr;
        other.size_ = 0;
    }
    MmapRegion& operator=(MmapRegion&& other) noexcept {
        if (this != &other) {
            if (addr_ != nullptr) ::munmap(addr_, size_);
            addr_ = other.addr_;
            size_ = other.size_;
            other.addr_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::byte* data() noexcept { return addr_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }

    [[nodiscard]] std::vector<unsigned char> query_residency(size_t page_size = 4096) const {
        const size_t num_pages = (size_ + page_size - 1) / page_size;
        std::vector<unsigned char> vec(num_pages, 0);
        if (::mincore(addr_, size_, vec.data()) != 0) {
            throw std::system_error(errno, std::generic_category(), "mincore failed");
        }
        return vec;
    }

private:
    std::byte* addr_{nullptr};
    size_t size_{0};
};

int main() {
    constexpr size_t page_size = 4096;
    constexpr size_t num_pages = 16;
    constexpr size_t alloc_size = num_pages * page_size;

    try {
        MmapRegion region(alloc_size);
        std::cout << "=== Перевірка резидентності сторінок через C++ RAII та mincore() ===\n";

        auto vec_initial = region.query_residency(page_size);
        size_t initial_count = 0;
        for (auto b : vec_initial) {
            if (b & 1) ++initial_count;
        }
        std::cout << "1. Після алокації: " << initial_count << " з " << num_pages << " сторінок у RAM\n";

        /* Звертаємося до парних сторінок */
        std::byte* raw = region.data();
        for (size_t i = 0; i < num_pages; i += 2) {
            raw[i * page_size] = static_cast<std::byte>(i + 1);
        }

        auto vec_active = region.query_residency(page_size);
        size_t active_count = 0;
        std::cout << "2. Карта сторінок після часткового доступу:\n   ";
        for (size_t i = 0; i < vec_active.size(); ++i) {
            bool in_ram = (vec_active[i] & 1) != 0;
            if (in_ram) ++active_count;
            std::cout << "P" << i << ":" << (in_ram ? "[RAM]" : "[---]") << " ";
        }
        std::cout << "\n   Активна робоча множина: " << active_count << " сторінок ("
                  << (active_count * page_size) / 1024 << " kB)\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
