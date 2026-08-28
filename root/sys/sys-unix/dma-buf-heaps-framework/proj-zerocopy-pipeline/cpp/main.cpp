#include <iostream>
#include <memory>
#include <expected>
#include <system_error>
#include <array>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/dma-heap.h>
#include <linux/videodev2.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm_fourcc.h>

class DmaBuffer {
    int fd_ = -1;
    std::size_t size_ = 0;

public:
    DmaBuffer() noexcept = default;
    DmaBuffer(int fd, std::size_t size) noexcept : fd_(fd), size_(size) {}
    ~DmaBuffer() { reset(); }

    DmaBuffer(const DmaBuffer&) = delete;
    DmaBuffer& operator=(const DmaBuffer&) = delete;

    DmaBuffer(DmaBuffer&& other) noexcept : fd_(other.release()), size_(other.size_) {
        other.size_ = 0;
    }

    DmaBuffer& operator=(DmaBuffer&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.release();
            size_ = other.size_;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] std::size_t size() const noexcept { return size_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
        size_ = 0;
    }
};

std::expected<DmaBuffer, std::error_code> allocate_cma_buffer(std::size_t size) {
    int heap_fd = ::open("/dev/dma_heap/linux,cma", O_RDONLY | O_CLOEXEC);
    if (heap_fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    dma_heap_allocation_data alloc_data{};
    alloc_data.len = size;
    alloc_data.fd_flags = O_RDWR | O_CLOEXEC;
    alloc_data.heap_flags = 0;

    if (::ioctl(heap_fd, DMA_HEAP_IOC_ALLOC, &alloc_data) < 0) {
        int err = errno;
        ::close(heap_fd);
        return std::unexpected(std::error_code(err, std::generic_category()));
    }

    ::close(heap_fd);
    return DmaBuffer(static_cast<int>(alloc_data.fd), size);
}

std::expected<void, std::error_code> queue_v4l2_dmabuf(int v4l2_fd, const DmaBuffer& buf, uint32_t index) {
    v4l2_buffer vbuf{};
    vbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    vbuf.memory = V4L2_MEMORY_DMABUF;
    vbuf.index = index;
    vbuf.m.fd = buf.get();

    if (::ioctl(v4l2_fd, VIDIOC_QBUF, &vbuf) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

std::expected<uint32_t, std::error_code> create_drm_fb_from_dmabuf(int drm_fd, const DmaBuffer& buf, uint32_t width, uint32_t height, uint32_t pitch) {
    drm_prime_handle prime{};
    prime.fd = buf.get();

    if (::ioctl(drm_fd, DRM_IOCTL_PRIME_FD_TO_HANDLE, &prime) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    uint32_t fb_id = 0;
    std::array<uint32_t, 4> handles = { prime.handle, 0, 0, 0 };
    std::array<uint32_t, 4> pitches = { pitch, 0, 0, 0 };
    std::array<uint32_t, 4> offsets = { 0, 0, 0, 0 };

    if (::drmModeAddFB2(drm_fd, width, height, DRM_FORMAT_XRGB8888,
                        handles.data(), pitches.data(), offsets.data(), &fb_id, 0) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return fb_id;
}

int main() {
    constexpr uint32_t width = 1920;
    constexpr uint32_t height = 1080;
    constexpr uint32_t pitch = width * 4;
    constexpr std::size_t buffer_size = static_cast<std::size_t>(pitch) * height;

    std::cout << "=== Старт zero-copy конвеєра dma-buf heaps (C++23) ===\n";

    auto result = allocate_cma_buffer(buffer_size);
    if (!result) {
        std::cerr << "Помилка виділення DMA пам'яті: " << result.error().message() << '\n';
        return 1;
    }

    DmaBuffer buffer = std::move(*result);
    std::cout << "Успішно отримано dma-buf fd: " << buffer.get() 
              << " (" << buffer.size() << " байтів)\n";

    return 0;
}
