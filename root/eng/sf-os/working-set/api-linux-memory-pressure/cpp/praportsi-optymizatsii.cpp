#include <iostream>
#include <vector>
#include <sys/mman.h>
#include <unistd.h>
#include <cstring>
#include <system_error>

class ManagedBuffer {
public:
    explicit ManagedBuffer(size_t size) : size_(size) {
        void* ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
        data_ = static_cast<std::byte*>(ptr);
    }

    ~ManagedBuffer() noexcept {
        if (data_ != nullptr) {
            ::munmap(data_, size_);
        }
    }

    void mark_cold() const {
        if (::madvise(data_, size_, MADV_COLD) != 0) {
            throw std::system_error(errno, std::generic_category(), "madvise(MADV_COLD) failed");
        }
    }

    void discard_pages() const {
        if (::madvise(data_, size_, MADV_DONTNEED) != 0) {
            throw std::system_error(errno, std::generic_category(), "madvise(MADV_DONTNEED) failed");
        }
    }

    [[nodiscard]] std::byte* data() noexcept { return data_; }
    [[nodiscard]] size_t size() const noexcept { return size_; }

private:
    std::byte* data_{nullptr};
    size_t size_{0};
};

int main() {
    constexpr size_t buffer_size = 16 * 1024 * 1024; // 16 МБ

    try {
        ManagedBuffer buffer(buffer_size);
        std::memset(buffer.data(), 0xAB, buffer.size());
        std::cout << "16 МБ пам'яті ініціалізовано.\n";

        buffer.mark_cold();
        std::cout << "MADV_COLD успішно застосовано через C++ RAII обгортку.\n";

        buffer.discard_pages();
        std::cout << "MADV_DONTNEED успішно вивільнив фізичні кадри.\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
