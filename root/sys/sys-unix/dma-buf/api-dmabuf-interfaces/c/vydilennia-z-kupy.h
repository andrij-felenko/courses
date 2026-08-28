int heap = open("/dev/dma_heap/system", O_RDONLY | O_CLOEXEC);
struct dma_heap_allocation_data a = {
        .len        = 4 << 20,
        .fd_flags   = O_RDWR | O_CLOEXEC,
        .heap_flags = 0,
};
if (ioctl(heap, DMA_HEAP_IOCTL_ALLOC, &a) < 0)
        return -1;
close(heap);                      /* буфер живе своїм дескриптором a.fd */

void *p = mmap(NULL, a.len, PROT_READ | PROT_WRITE, MAP_SHARED, a.fd, 0);

struct dma_buf_sync s = { .flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_WRITE };
while (ioctl(a.fd, DMA_BUF_IOCTL_SYNC, &s) < 0 && (errno == EINTR || errno == EAGAIN))
        ;
memset(p, 0, a.len);
s.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_WRITE;
while (ioctl(a.fd, DMA_BUF_IOCTL_SYNC, &s) < 0 && (errno == EINTR || errno == EAGAIN))
        ;
