#include <cstdint>
#include <cstddef>
#include <memory>
#include <stdexcept>
#include <span>

#if defined(_WIN32)
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

class ExecutableBuffer {
public:
    explicit ExecutableBuffer(std::size_t capacity)
        : capacity_(capacity), size_(0), buffer_(nullptr) {
#if defined(_WIN32)
        buffer_ = static_cast<uint8_t*>(VirtualAlloc(
            nullptr, capacity_, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE));
        if (!buffer_) {
            throw std::runtime_error("VirtualAlloc failed to allocate executable memory");
        }
#else
        void* ptr = mmap(nullptr, capacity_, 
                         PROT_READ | PROT_WRITE | PROT_EXEC, 
                         MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::runtime_error("mmap failed to allocate executable memory");
        }
        buffer_ = static_cast<uint8_t*>(ptr);
#endif
    }

    ~ExecutableBuffer() noexcept {
        if (buffer_) {
#if defined(_WIN32)
            VirtualFree(buffer_, 0, MEM_RELEASE);
#else
            munmap(buffer_, capacity_);
#endif
        }
    }

    ExecutableBuffer(const ExecutableBuffer&) = delete;
    ExecutableBuffer& operator=(const ExecutableBuffer&) = delete;

    ExecutableBuffer(ExecutableBuffer&& other) noexcept
        : capacity_(other.capacity_), size_(other.size_), buffer_(other.buffer_) {
        other.buffer_ = nullptr;
        other.size_ = 0;
    }

    uint8_t* allocate_block(std::size_t bytes) {
        if (size_ + bytes > capacity_) {
            throw std::runtime_error("Code cache memory overflow");
        }
        uint8_t* ptr = buffer_ + size_;
        size_ += bytes;
        return ptr;
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }

private:
    std::size_t capacity_;
    std::size_t size_;
    uint8_t*    buffer_;
};
