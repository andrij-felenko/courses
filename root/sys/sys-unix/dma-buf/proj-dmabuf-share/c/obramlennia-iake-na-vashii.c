static void sync_buf(int fd, __u64 flags)
{
    struct dma_buf_sync s = { .flags = flags };
    int r;
    do { r = ioctl(fd, DMA_BUF_IOCTL_SYNC, &s); } while (r < 0 && (errno == EINTR || errno == EAGAIN));
    if (r < 0) die("DMA_BUF_IOCTL_SYNC");
}

static void sync_start(int fd, __u64 rw) { sync_buf(fd, rw | DMA_BUF_SYNC_START); }
static void sync_end(int fd, __u64 rw)   { sync_buf(fd, rw | DMA_BUF_SYNC_END); }
