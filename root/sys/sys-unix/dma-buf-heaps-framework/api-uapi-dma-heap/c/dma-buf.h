#include <linux/dma-buf.h>

struct dma_buf_sync sync = {
    .flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_RW
};
ioctl(dma_buf_fd, DMA_BUF_IOCTL_SYNC, &sync);

/* читання або запис даних у mmap-вказівник */

sync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_RW;
ioctl(dma_buf_fd, DMA_BUF_IOCTL_SYNC, &sync);
