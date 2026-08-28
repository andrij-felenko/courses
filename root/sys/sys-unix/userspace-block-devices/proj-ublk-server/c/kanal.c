/* Описи — у спільній пам'яті; буфери — наші й на весь час життя пристрою. */
static int open_channel(void)
{
        const long   page   = sysconf(_SC_PAGESIZE);
        /* крок між чергами — МАКСИМАЛЬНА глибина, а не наша: 4096 × 24 Б = 96 КіБ */
        const size_t stride = UBLK_MAX_QUEUE_DEPTH * sizeof(struct ublksrv_io_desc);
        size_t len = QDEPTH * sizeof(struct ublksrv_io_desc);
        char path[64];
        unsigned t;

        len = (len + page - 1) & ~(size_t)(page - 1);
        snprintf(path, sizeof(path), "/dev/ublkc%u", info.dev_id);
        if ((cdev_fd = open(path, O_RDWR)) < 0)
                return -errno;

        desc = mmap(NULL, len, PROT_READ, MAP_SHARED | MAP_POPULATE,
                    cdev_fd, UBLKSRV_CMD_BUF_OFFSET + 0 * stride);   /* черга 0 */
        if (desc == MAP_FAILED)
                return -errno;

        for (t = 0; t < QDEPTH; t++) {
                if (posix_memalign((void **)&buf[t], page, IO_BUF_SZ))
                        return -ENOMEM;
                mlock(buf[t], IO_BUF_SZ);
        }
        return io_uring_queue_init(QDEPTH, &io_ring, 0);
}
