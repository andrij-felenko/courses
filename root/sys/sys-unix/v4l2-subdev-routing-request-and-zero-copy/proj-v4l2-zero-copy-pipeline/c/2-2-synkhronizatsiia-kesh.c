#include <linux/dma-buf.h>
#include <sys/ioctl.h>

struct dma_buf_sync sync;
memset(&sync, 0, sizeof(sync));

/* 1. Початок доступу ЦП на читання (Invalidate Cache Lines) */
sync.flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ;
if (ioctl(dmabuf_fd, DMABUF_IOCTL_SYNC, &sync) < 0) {
    perror("DMABUF_IOCTL_SYNC START failed");
}

/* Безпосереднє читання байтів з start */
unsigned char first_byte = ((unsigned char*)buffer_start)[0];

/* 2. Завершення доступу ЦП */
sync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
ioctl(dmabuf_fd, DMABUF_IOCTL_SYNC, &sync);
