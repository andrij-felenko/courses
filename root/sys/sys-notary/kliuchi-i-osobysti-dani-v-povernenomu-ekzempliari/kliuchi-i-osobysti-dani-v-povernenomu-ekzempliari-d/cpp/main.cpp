#include <sys/mman.h>
#include <sys/prctl.h>
#include <span>
#include <memory>
#include <system_error>
#include <concepts>

/* RAII-обгортка для криптографічно захищеного регіону RAM */
class SecureMemoryRegion {
public:
    explicit SecureMemoryRegion(std::size_t size) : size_(size), data_(nullptr) {
        if (size_ == 0) return;

        void* raw_ptr = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE,
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (raw_ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }

        data_ = static_cast<std::byte*>(raw_ptr);

        if (::mlock(data_, size_) != 0) {
            ::munmap(data_, size_);
            throw std::system_error(errno, std::generic_category(), "mlock failed");
        }

        if (::madvise(data_, size_, MADV_DONTDUMP) != 0) {
            ::munlock(data_, size_);
            ::munmap(data_, size_);
            throw std::system_error(errno, std::generic_category(), "madvise MADV_DONTDUMP failed");
        }

        ::prctl(PR_SET_DUMPABLE, 0);
    }

    ~SecureMemoryRegion() noexcept {
        if (data_ && size_ > 0) {
            // Гарантоване занулення перед поверненням пам'яті системі
            volatile auto* p = reinterpret_cast<volatile std::byte*>(data_);
            for (std::size_t i = 0; i < size_; ++i) {
                p[i] = std::byte{0};
            }
            #if defined(__GNUC__) || defined(__clang__)
            asm volatile("" : : "r"(data_) : "memory");
            #endif

            ::munlock(data_, size_);
            ::munmap(data_, size_);
        }
    }

    [[nodiscard]] std::span<std::byte> span() noexcept {
        return {data_, size_};
    }

    SecureMemoryRegion(const SecureMemoryRegion&) = delete;
    SecureMemoryRegion& operator=(const SecureMemoryRegion&) = delete;
    SecureMemoryRegion(SecureMemoryRegion&& other) noexcept 
        : size_(other.size_), data_(other.data_) {
        other.size_ = 0;
        other.data_ = nullptr;
    }
    SecureMemoryRegion& operator=(SecureMemoryRegion&& other) noexcept {
        if (this != &other) {
            this->~SecureMemoryRegion();
            size_ = other.size_;
            data_ = other.data_;
            other.size_ = 0;
            other.data_ = nullptr;
        }
        return *this;
    }

private:
    std::size_t size_;
    std::byte* data_;
};
