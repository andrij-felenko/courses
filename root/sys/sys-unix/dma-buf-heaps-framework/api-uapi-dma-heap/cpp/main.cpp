#include <iostream>
#include <string>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/dma-heap.h>

class UniqueFd {
    int fd_ = -1;
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

std::expected<UniqueFd, std::error_code> allocate_dma_buffer(const std::string& heap_path, std::size_t size) {
    UniqueFd heap_fd(::open(heap_path.c_str(), O_RDONLY | O_CLOEXEC));
    if (!heap_fd.valid()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    dma_heap_allocation_data alloc_data{};
    alloc_data.len = size;
    alloc_data.fd_flags = O_RDWR | O_CLOEXEC;
    alloc_data.heap_flags = 0;

    if (::ioctl(heap_fd.get(), DMA_HEAP_IOC_ALLOC, &alloc_data) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return UniqueFd(static_cast<int>(alloc_data.fd));
}
