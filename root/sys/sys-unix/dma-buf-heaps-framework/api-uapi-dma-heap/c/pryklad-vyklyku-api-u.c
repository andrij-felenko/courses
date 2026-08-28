#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/dma-heap.h>
#include <errno.h>

int allocate_dma_buffer(const char *heap_path, size_t size) {
    int heap_fd = open(heap_path, O_RDONLY | O_CLOEXEC);
    if (heap_fd < 0) {
        perror("open dma_heap device failed");
        return -1;
    }

    struct dma_heap_allocation_data alloc_data = {
        .len = size,
        .fd = 0,
        .fd_flags = O_RDWR | O_CLOEXEC,
        .heap_flags = 0
    };

    if (ioctl(heap_fd, DMA_HEAP_IOC_ALLOC, &alloc_data) < 0) {
        perror("DMA_HEAP_IOC_ALLOC ioctl failed");
        close(heap_fd);
        return -1;
    }

    close(heap_fd);
    return alloc_data.fd;
}
