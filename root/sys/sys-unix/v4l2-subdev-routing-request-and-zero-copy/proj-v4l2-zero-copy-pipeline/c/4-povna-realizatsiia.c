#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/media.h>
#include <linux/v4l2-subdev.h>
#include <linux/videodev2.h>
#include <linux/dma-buf.h>

#define BUFFER_COUNT 4

struct buffer {
    void *start;
    size_t length;
    int dbuf_fd;
};

int main(void) {
    int media_fd = -1;
    int subdev_fd = -1;
    int video_fd = -1;
    struct buffer buffers[BUFFER_COUNT];
    memset(buffers, 0, sizeof(buffers));

    /* 1. Відкриття Media Controller та аналіз графа */
    media_fd = open("/dev/media0", O_RDWR);
    if (media_fd < 0) {
        perror("Не вдалося відкрити /dev/media0");
        return EXIT_FAILURE;
    }

    struct media_device_info dev_info;
    memset(&dev_info, 0, sizeof(dev_info));
    if (ioctl(media_fd, MEDIA_IOC_DEVICE_INFO, &dev_info) < 0) {
        perror("MEDIA_IOC_DEVICE_INFO помилка");
        goto cleanup;
    }
    printf("[C] Медіа-пристрій: %s (%s), шина: %s\n", 
           dev_info.driver, dev_info.model, dev_info.bus_info);

    /* 2. Відкриття та налаштування Subdevice Pad Format */
    subdev_fd = open("/dev/v4l2-subdev0", O_RDWR);
    if (subdev_fd < 0) {
        perror("Не вдалося відкрити /dev/v4l2-subdev0");
        goto cleanup;
    }

    struct v4l2_subdev_format fmt;
    memset(&fmt, 0, sizeof(fmt));
    fmt.pad = 0; /* Source pad */
    fmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
    fmt.format.width = 1920;
    fmt.format.height = 1080;
    fmt.format.code = MEDIA_BUS_FMT_UYVY8_2X8;
    fmt.format.field = V4L2_FIELD_NONE;

    if (ioctl(subdev_fd, VIDIOC_SUBDEV_S_FMT, &fmt) < 0) {
        perror("VIDIOC_SUBDEV_S_FMT помилка");
        goto cleanup;
    }
    printf("[C] Subdev Pad format встановлено: %dx%d (code 0x%x)\n",
           fmt.format.width, fmt.format.height, fmt.format.code);

    /* 3. Відкриття відеовузла захоплення /dev/video0 */
    video_fd = open("/dev/video0", O_RDWR | O_NONBLOCK);
    if (video_fd < 0) {
        perror("Не вдалося відкрити /dev/video0");
        goto cleanup;
    }

    struct v4l2_format vfmt;
    memset(&vfmt, 0, sizeof(vfmt));
    vfmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    vfmt.fmt.pix.width = 1920;
    vfmt.fmt.pix.height = 1080;
    vfmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
    vfmt.fmt.pix.field = V4L2_FIELD_NONE;

    if (ioctl(video_fd, VIDIOC_S_FMT, &vfmt) < 0) {
        perror("VIDIOC_S_FMT помилка");
        goto cleanup;
    }

    /* 4. Запит буферів у ядра (REQBUFS) */
    struct v4l2_requestbuffers req;
    memset(&req, 0, sizeof(req));
    req.count = BUFFER_COUNT;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;

    if (ioctl(video_fd, VIDIOC_REQBUFS, &req) < 0) {
        perror("VIDIOC_REQBUFS помилка");
        goto cleanup;
    }

    /* 5. Відображення буферів (mmap) та експорт у DMA-BUF (VIDIOC_EXPBUF) */
    for (size_t i = 0; i < req.count; ++i) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;

        if (ioctl(video_fd, VIDIOC_QUERYBUF, &buf) < 0) {
            perror("VIDIOC_QUERYBUF помилка");
            goto cleanup;
        }

        buffers[i].length = buf.length;
        buffers[i].start = mmap(NULL, buf.length,
                                PROT_READ | PROT_WRITE,
                                MAP_SHARED, video_fd, buf.m.offset);
        if (buffers[i].start == MAP_FAILED) {
            perror("mmap помилка");
            goto cleanup;
        }

        struct v4l2_exportbuffer expbuf;
        memset(&expbuf, 0, sizeof(expbuf));
        expbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        expbuf.index = i;
        expbuf.flags = O_CLOEXEC | O_RDWR;

        if (ioctl(video_fd, VIDIOC_EXPBUF, &expbuf) < 0) {
            perror("VIDIOC_EXPBUF помилка");
            goto cleanup;
        }
        buffers[i].dbuf_fd = expbuf.fd;
        printf("[C] Буфер %zu експортовано як dma-buf fd: %d\n", i, expbuf.fd);
    }

    /* 6. Постановка буферів у чергу та запуск відеопотоку */
    for (size_t i = 0; i < req.count; ++i) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        if (ioctl(video_fd, VIDIOC_QBUF, &buf) < 0) {
            perror("VIDIOC_QBUF помилка");
            goto cleanup;
        }
    }

    enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (ioctl(video_fd, VIDIOC_STREAMON, &type) < 0) {
        perror("VIDIOC_STREAMON помилка");
        goto cleanup;
    }

    /* 7. Очікування та вилучення одного кадру (poll + DQBUF) */
    struct pollfd pfd;
    pfd.fd = video_fd;
    pfd.events = POLLIN;

    int poll_res = poll(&pfd, 1, 2000);
    if (poll_res > 0 && (pfd.revents & POLLIN)) {
        struct v4l2_buffer dqbuf;
        memset(&dqbuf, 0, sizeof(dqbuf));
        dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        dqbuf.memory = V4L2_MEMORY_MMAP;

        if (ioctl(video_fd, VIDIOC_DQBUF, &dqbuf) < 0) {
            perror("VIDIOC_DQBUF помилка");
            goto cleanup;
        }
        printf("[C] Захоплено кадр №%u, розмір: %u байт\n", dqbuf.sequence, dqbuf.bytesused);

        /* Синхронізація кешу ЦП перед читанням перших байтів */
        struct dma_buf_sync dsync;
        memset(&dsync, 0, sizeof(dsync));
        dsync.flags = DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ;
        ioctl(buffers[dqbuf.index].dbuf_fd, DMABUF_IOCTL_SYNC, &dsync);

        printf("[C] Перші байти кадру: %02x %02x %02x %02x\n",
               ((unsigned char*)buffers[dqbuf.index].start)[0],
               ((unsigned char*)buffers[dqbuf.index].start)[1],
               ((unsigned char*)buffers[dqbuf.index].start)[2],
               ((unsigned char*)buffers[dqbuf.index].start)[3]);

        dsync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
        ioctl(buffers[dqbuf.index].dbuf_fd, DMABUF_IOCTL_SYNC, &dsync);
    }

    /* Зупинка потоку */
    ioctl(video_fd, VIDIOC_STREAMOFF, &type);

cleanup:
    for (size_t i = 0; i < BUFFER_COUNT; ++i) {
        if (buffers[i].dbuf_fd >= 0) close(buffers[i].dbuf_fd);
        if (buffers[i].start && buffers[i].start != MAP_FAILED) {
            munmap(buffers[i].start, buffers[i].length);
        }
    }
    if (video_fd >= 0) close(video_fd);
    if (subdev_fd >= 0) close(subdev_fd);
    if (media_fd >= 0) close(media_fd);

    return 0;
}
