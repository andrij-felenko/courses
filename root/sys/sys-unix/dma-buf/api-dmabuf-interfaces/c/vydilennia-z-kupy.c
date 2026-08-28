struct dma_heap_allocation_data {
        __u64 len;
        __u32 fd;                 /* заповнює ядро */
        __u32 fd_flags;
        __u64 heap_flags;
};

#define DMA_HEAP_VALID_FD_FLAGS    (O_CLOEXEC | O_ACCMODE)
#define DMA_HEAP_VALID_HEAP_FLAGS  (0ULL)
#define DMA_HEAP_IOC_MAGIC         'H'
#define DMA_HEAP_IOCTL_ALLOC       _IOWR(DMA_HEAP_IOC_MAGIC, 0x0, \
                                         struct dma_heap_allocation_data)
