#include <linux/dma-buf.h>
#include <sys/ioctl.h>
#include <system_error>

dma_buf_sync sync{};
sync.flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ;

if (::ioctl(dmabuf_fd, DMABUF_IOCTL_SYNC, &sync) < 0) {
    throw std::system_error(errno, std::generic_category(), "DMABUF_IOCTL_SYNC START failed");
}

// Читання кадрів ЦП у C++
uint8_t first_byte = static_cast<const uint8_t*>(buffer_start)[0];

sync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
::ioctl(dmabuf_fd, DMABUF_IOCTL_SYNC, &sync);
