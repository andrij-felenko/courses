/* dmabuf-demo.c — один буфер із купи dma-heap на два незалежні процеси. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/dma-buf.h>
#include <linux/dma-heap.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#define HEAP     "/dev/dma_heap/system"
#define SOCKNAME "dmabuf-demo"        /* абстрактна адреса: без сліду у файловій системі */
#define BYTES    (1u << 20)           /* мегабайт корисних даних */

static void die(const char *what) { perror(what); exit(1); }

/* Заголовок, що їде поруч із дескриптором. */
struct handoff {
    uint64_t bytes;                   /* скільки байтів у буфері справді наші */
    uint32_t seed;                    /* із чого пораховано візерунок */
};

static uint32_t word_at(uint32_t seed, size_t i)
{
    return seed + (uint32_t)i * 2654435761u;
}

static int heap_alloc(uint64_t bytes)
{
    int heap = open(HEAP, O_RDONLY | O_CLOEXEC);
    if (heap < 0) die("open " HEAP);

    struct dma_heap_allocation_data req = {
        .len        = bytes,
        .fd_flags   = O_RDWR | O_CLOEXEC,  /* без O_RDWR mmap на запис не дадуть */
        .heap_flags = 0,
    };
    if (ioctl(heap, DMA_HEAP_IOCTL_ALLOC, &req) < 0) die("DMA_HEAP_IOCTL_ALLOC");

    close(heap);       /* буфер тримається сам; купа більше ні для чого не потрібна */
    return req.fd;
}
