#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/dma-heap.h>
#include <linux/videodev2.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm_fourcc.h>
#include <errno.h>

/* Функція виділення неперервного DMA буфера з CMA купи */
int allocate_cma_buffer(size_t size) {
    int heap_fd = open("/dev/dma_heap/linux,cma", O_RDONLY | O_CLOEXEC);
    if (heap_fd < 0) {
        perror("Не вдалося відкрити CMA heap /dev/dma_heap/linux,cma");
        return -1;
    }

    struct dma_heap_allocation_data alloc_data = {
        .len = size,
        .fd = 0,
        .fd_flags = O_RDWR | O_CLOEXEC,
        .heap_flags = 0
    };

    if (ioctl(heap_fd, DMA_HEAP_IOC_ALLOC, &alloc_data) < 0) {
        perror("Збій ioctl DMA_HEAP_IOC_ALLOC для CMA");
        close(heap_fd);
        return -1;
    }

    close(heap_fd);
    return alloc_data.fd;
}

/* Передача буфера dma-buf у чергу V4L2 камери */
int queue_v4l2_dmabuf(int v4l2_fd, int dmabuf_fd, uint32_t index) {
    struct v4l2_buffer buf;
    memset(&buf, 0, sizeof(buf));
    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf.memory = V4L2_MEMORY_DMABUF;
    buf.index = index;
    buf.m.fd = dmabuf_fd;

    if (ioctl(v4l2_fd, VIDIOC_QBUF, &buf) < 0) {
        perror("Збій ioctl VIDIOC_QBUF V4L2_MEMORY_DMABUF");
        return -1;
    }
    return 0;
}

/* Імпорт dma-buf у DRM підсистему та створення фреймбуфера */
uint32_t create_drm_fb_from_dmabuf(int drm_fd, int dmabuf_fd, uint32_t width, uint32_t height, uint32_t pitch) {
    struct drm_prime_handle prime;
    memset(&prime, 0, sizeof(prime));
    prime.fd = dmabuf_fd;

    if (ioctl(drm_fd, DRM_IOCTL_PRIME_FD_TO_HANDLE, &prime) < 0) {
        perror("Збій DRM_IOCTL_PRIME_FD_TO_HANDLE");
        return 0;
    }

    uint32_t fb_id = 0;
    uint32_t handles[4] = { prime.handle, 0, 0, 0 };
    uint32_t pitches[4] = { pitch, 0, 0, 0 };
    uint32_t offsets[4] = { 0, 0, 0, 0 };

    if (drmModeAddFB2(drm_fd, width, height, DRM_FORMAT_XRGB8888,
                      handles, pitches, offsets, &fb_id, 0) < 0) {
        perror("Збій drmModeAddFB2");
        return 0;
    }

    return fb_id;
}

int main(void) {
    uint32_t width = 1920;
    uint32_t height = 1080;
    uint32_t pitch = width * 4;
    size_t buffer_size = (size_t)pitch * height;

    printf("=== Старт zero-copy конвеєра dma-buf heaps ===\n");

    int dmabuf_fd = allocate_cma_buffer(buffer_size);
    if (dmabuf_fd < 0) {
        fprintf(stderr, "Помилка: не вдалося виділити неперервний DMA буфер\n");
        return EXIT_FAILURE;
    }

    printf("Успішно отримано dma-buf fd: %d (розмір: %zu байтів)\n", dmabuf_fd, buffer_size);

    /* Імітація завершення роботи zero-copy конвеєра */
    close(dmabuf_fd);
    printf("Конвеєр завершив роботу без копіювання пам'яті.\n");
    return EXIT_SUCCESS;
}
