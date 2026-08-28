// Захищений RAII-буфер пам'яті для секретів мовою C++
#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>
#include <cstring>
#include <span>
#include <memory>
#include <iostream>
#include <stdexcept>

class SecureMemory {
    void* ptr_{nullptr};
    std::size_t size_{0};

    static std::size_t align_to_page(std::size_t req_size) noexcept {
        const auto page_sz = static_cast<std::size_t>(::sysconf(_SC_PAGESIZE));
        return (req_size + page_sz - 1) & ~(page_sz - 1);
    }
public:
    explicit SecureMemory(std::size_t size) : size_(align_to_page(size)) {
        ptr_ = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (ptr_ == MAP_FAILED) {
            throw std::runtime_error("mmap failed");
        }

        // 1. Блокування сторінки від вивантаження у swap
        ::mlock(ptr_, size_);

        // 2. Виключення пам'яті з coredump дампів
        ::madvise(ptr_, size_, MADV_DONTDUMP);
    }

    ~SecureMemory() {
        if (ptr_ && ptr_ != MAP_FAILED) {
            // 3. Гарантоване занулення байтів у пам'яті
            ::explicit_bzero(ptr_, size_);
            ::munlock(ptr_, size_);
            ::munmap(ptr_, size_);
        }
    }

    SecureMemory(const SecureMemory&) = delete;
    SecureMemory& operator=(const SecureMemory&) = delete;

    SecureMemory(SecureMemory&& other) noexcept : ptr_(other.ptr_), size_(other.size_) {
        other.ptr_ = nullptr;
        other.size_ = 0;
    }

    SecureMemory& operator=(SecureMemory&& other) noexcept {
        if (this != &other) {
            this->~SecureMemory();
            ptr_ = other.ptr_;
            size_ = other.size_;
            other.ptr_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::span<std::byte> bytes() noexcept {
        return {static_cast<std::byte*>(ptr_), size_};
    }
};
