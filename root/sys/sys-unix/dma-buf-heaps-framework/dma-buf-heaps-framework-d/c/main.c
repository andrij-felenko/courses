#include <linux/dma-buf.h>
#include <sys/ioctl.h>

void process_buffer_cpu(int dmabuf_fd, void *ptr, size_t size) {
    struct dma_buf_sync sync = {0};

    /* 1. Початок доступу CPU на читання та запис */
    sync.flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_RW;
    ioctl(dmabuf_fd, DMA_BUF_IOCTL_SYNC, &sync);

    /* Модифікація даних процесором */
    memset(ptr, 0xAB, size);

    /* 2. Завершення доступу CPU (примусове скидання кешу у RAM) */
    sync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_RW;
    ioctl(dmabuf_fd, DMA_BUF_IOCTL_SYNC, &sync);
}
