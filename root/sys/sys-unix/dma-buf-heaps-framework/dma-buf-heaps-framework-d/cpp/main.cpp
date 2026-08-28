#include <linux/dma-buf.h>
#include <sys/ioctl.h>
#include <system_error>
#include <cstring>

void process_buffer_cpu(int dmabuf_fd, void* ptr, std::size_t size) {
    dma_buf_sync sync{};

    // 1. Початок доступу CPU на читання та запис
    sync.flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_RW;
    if (::ioctl(dmabuf_fd, DMA_BUF_IOCTL_SYNC, &sync) < 0) {
        throw std::system_error(errno, std::generic_category(), "DMA_BUF_SYNC_START failed");
    }

    // Модифікація даних процесором
    std::memset(ptr, 0xAB, size);

    // 2. Завершення доступу CPU (примусове скидання кешу у RAM)
    sync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_RW;
    if (::ioctl(dmabuf_fd, DMA_BUF_IOCTL_SYNC, &sync) < 0) {
        throw std::system_error(errno, std::generic_category(), "DMA_BUF_SYNC_END failed");
    }
}
