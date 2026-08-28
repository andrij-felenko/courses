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

#define BUF_COUNT 4

struct buffer_entry {
    void *start;
    size_t length;
    int dbuf_fd;
};

int main(void) {
    int media_fd = -1, subdev_fd = -1, video_fd = -1;
    struct buffer_entry buffers[BUF_COUNT];
    memset(buffers, 0, sizeof(buffers));

    /* 1. Відкриття media-контролера та зчитування топології */
    media_fd = open("/dev/media0", O_RDWR);
    if (media_fd < 0) {
        perror("open /dev/media0 failed");
        return EXIT_FAILURE;
    }

    struct media_device_info minfo;
    memset(&minfo, 0, sizeof(minfo));
    if (ioctl(media_fd, MEDIA_IOC_DEVICE_INFO, &minfo) < 0) {
        perror("MEDIA_IOC_DEVICE_INFO failed");
        goto cleanup;
    }
    printf("[C] Connected to media dev: %s (%s)\n", minfo.driver, minfo.model);

    /* 2. Налаштування субпристрою */
    subdev_fd = open("/dev/v4l2-subdev0", O_RDWR);
    if (subdev_fd < 0) {
        perror("open /dev/v4l2-subdev0 failed");
        goto cleanup;
    }

    struct v4l2_subdev_format sfmt;
    memset(&sfmt, 0, sizeof(sfmt));
    sfmt.pad = 0;
    sfmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
    sfmt.format.width = 1920;
    sfmt.format.height = 1080;
    sfmt.format.code = MEDIA_BUS_FMT_UYVY8_2X8;
    sfmt.format.field = V4L2_FIELD_NONE;

    if (ioctl(subdev_fd, VIDIOC_SUBDEV_S_FMT, &sfmt) < 0) {
        perror("VIDIOC_SUBDEV_S_FMT failed");
        goto cleanup;
    }

    /* 3. Налаштування вузла захоплення /dev/video0 */
    video_fd = open("/dev/video0", O_RDWR | O_NONBLOCK);
    if (video_fd < 0) {
        perror("open /dev/video0 failed");
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
        perror("VIDIOC_S_FMT failed");
        goto cleanup;
    }

    /* 4. Запит буферів у ядра */
    struct v4l2_requestbuffers req;
    memset(&req, 0, sizeof(req));
    req.count = BUF_COUNT;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req.memory = V4L2_MEMORY_MMAP;

    if (ioctl(video_fd, VIDIOC_REQBUFS, &req) < 0) {
        perror("VIDIOC_REQBUFS failed");
        goto cleanup;
    }

    for (size_t i = 0; i < req.count; ++i) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;

        if (ioctl(video_fd, VIDIOC_QUERYBUF, &buf) < 0) {
            perror("VIDIOC_QUERYBUF failed");
            goto cleanup;
        }

        buffers[i].length = buf.length;
        buffers[i].start = mmap(NULL, buf.length, PROT_READ | PROT_WRITE,
                                MAP_SHARED, video_fd, buf.m.offset);
        if (buffers[i].start == MAP_FAILED) {
            perror("mmap failed");
            goto cleanup;
        }

        struct v4l2_exportbuffer expbuf;
        memset(&expbuf, 0, sizeof(expbuf));
        expbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        expbuf.index = i;
        expbuf.flags = O_CLOEXEC | O_RDWR;

        if (ioctl(video_fd, VIDIOC_EXPBUF, &expbuf) < 0) {
            perror("VIDIOC_EXPBUF failed");
            goto cleanup;
        }
        buffers[i].dbuf_fd = expbuf.fd;
    }

    /* 5. Запуск потоку та зчитування одного кадру через poll */
    for (size_t i = 0; i < req.count; ++i) {
        struct v4l2_buffer buf;
        memset(&buf, 0, sizeof(buf));
        buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        buf.memory = V4L2_MEMORY_MMAP;
        buf.index = i;
        ioctl(video_fd, VIDIOC_QBUF, &buf);
    }

    enum v4l2_buf_type stype = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (ioctl(video_fd, VIDIOC_STREAMON, &stype) < 0) {
        perror("VIDIOC_STREAMON failed");
        goto cleanup;
    }

    struct pollfd pfd;
    pfd.fd = video_fd;
    pfd.events = POLLIN;

    int poll_res = poll(&pfd, 1, 2000); /* Очікування 2 секунди */
    if (poll_res > 0 && (pfd.revents & POLLIN)) {
        struct v4l2_buffer dqbuf;
        memset(&dqbuf, 0, sizeof(dqbuf));
        dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        dqbuf.memory = V4L2_MEMORY_MMAP;

        if (ioctl(video_fd, VIDIOC_DQBUF, &dqbuf) == 0) {
            printf("[C] Captured frame seq %u, size %u bytes\n", dqbuf.sequence, dqbuf.bytesused);
        }
    } else {
        printf("[C] Poll timeout or error\n");
    }

    ioctl(video_fd, VIDIOC_STREAMOFF, &stype);

cleanup:
    for (size_t i = 0; i < BUF_COUNT; ++i) {
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
