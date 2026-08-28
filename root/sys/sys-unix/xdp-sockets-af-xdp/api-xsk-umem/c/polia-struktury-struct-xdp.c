#include <sys/socket.h>
#include <sys/mman.h>
#include <linux/if_xdp.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

int setup_umem(int xsk_fd, void **buffer_out, size_t size) {
    void *buffer = NULL;
    if (posix_memalign(&buffer, getpagesize(), size) != 0) {
        perror("posix_memalign failed");
        return -1;
    }

    struct xdp_umem_reg mr = {
        .addr = (uintptr_t)buffer,
        .len = size,
        .chunk_size = 2048,
        .headroom = 0,
        .flags = 0
    };

    if (setsockopt(xsk_fd, SOL_XDP, XDP_UMEM_REG, &mr, sizeof(mr)) < 0) {
        perror("setsockopt(XDP_UMEM_REG) failed");
        free(buffer);
        return -1;
    }

    *buffer_out = buffer;
    return 0;
}
