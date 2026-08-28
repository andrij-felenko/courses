#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <poll.h>
#include <linux/videodev2.h>

#define SRC_W 1920
#define SRC_H 1080
#define DST_W 640
#define DST_H 480

struct buffer_info {
    void *start;
    size_t length;
};

static int xioctl(int fd, unsigned long request, void *arg) {
    int r;
    do {
        r = ioctl(fd, request, arg);
    } while (r == -1 && errno == EINTR);
    return r;
}

int main(int argc, char **argv) {
    const char *dev_name = (argc > 1) ? argv[1] : "/dev/video10";
    int fd = open(dev_name, O_RDWR | O_NONBLOCK);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій V4L2 M2M");
        return EXIT_FAILURE;
    }

    struct v4l2_capability cap;
    memset(&cap, 0, sizeof(cap));
    if (xioctl(fd, VIDIOC_QUERYCAP, &cap) < 0) {
        perror("VIDIOC_QUERYCAP помилка");
        close(fd);
        return EXIT_FAILURE;
    }

    if (!(cap.capabilities & (V4L2_CAP_VIDEO_M2M | V4L2_CAP_STREAMING))) {
        fprintf(stderr, "Пристрій не підтримує інтерфейс V4L2 M2M потоків\n");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 1. Налаштування формату черги OUTPUT (Вхідні дані) */
    struct v4l2_format fmt_out;
    memset(&fmt_out, 0, sizeof(fmt_out));
    fmt_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
    fmt_out.fmt.pix.width = SRC_W;
    fmt_out.fmt.pix.height = SRC_H;
    fmt_out.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
    fmt_out.fmt.pix.field = V4L2_FIELD_NONE;
    if (xioctl(fd, VIDIOC_S_FMT, &fmt_out) < 0) {
        perror("Помилка встановлення формату OUTPUT");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 2. Налаштування формату черги CAPTURE (Вихідні дані) */
    struct v4l2_format fmt_cap;
    memset(&fmt_cap, 0, sizeof(fmt_cap));
    fmt_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt_cap.fmt.pix.width = DST_W;
    fmt_cap.fmt.pix.height = DST_H;
    fmt_cap.fmt.pix.pixelformat = V4L2_PIX_FMT_NV12;
    fmt_cap.fmt.pix.field = V4L2_FIELD_NONE;
    if (xioctl(fd, VIDIOC_S_FMT, &fmt_cap) < 0) {
        perror("Помилка встановлення формату CAPTURE");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 3. Виділення буферів для черги OUTPUT */
    struct v4l2_requestbuffers req_out;
    memset(&req_out, 0, sizeof(req_out));
    req_out.count = 1;
    req_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
    req_out.memory = V4L2_MEMORY_MMAP;
    if (xioctl(fd, VIDIOC_REQBUFS, &req_out) < 0) {
        perror("Помилка REQBUFS OUTPUT");
        close(fd);
        return EXIT_FAILURE;
    }

    struct v4l2_buffer buf_out;
    memset(&buf_out, 0, sizeof(buf_out));
    buf_out.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
    buf_out.memory = V4L2_MEMORY_MMAP;
    buf_out.index = 0;
    if (xioctl(fd, VIDIOC_QUERYBUF, &buf_out) < 0) {
        perror("Помилка QUERYBUF OUTPUT");
        close(fd);
        return EXIT_FAILURE;
    }

    struct buffer_info src_buf;
    src_buf.length = buf_out.length;
    src_buf.start = mmap(NULL, buf_out.length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, buf_out.m.offset);
    if (src_buf.start == MAP_FAILED) {
        perror("Помилка mmap OUTPUT");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 4. Виділення буферів для черги CAPTURE */
    struct v4l2_requestbuffers req_cap;
    memset(&req_cap, 0, sizeof(req_cap));
    req_cap.count = 1;
    req_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    req_cap.memory = V4L2_MEMORY_MMAP;
    if (xioctl(fd, VIDIOC_REQBUFS, &req_cap) < 0) {
        perror("Помилка REQBUFS CAPTURE");
        munmap(src_buf.start, src_buf.length);
        close(fd);
        return EXIT_FAILURE;
    }

    struct v4l2_buffer buf_cap;
    memset(&buf_cap, 0, sizeof(buf_cap));
    buf_cap.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    buf_cap.memory = V4L2_MEMORY_MMAP;
    buf_cap.index = 0;
    if (xioctl(fd, VIDIOC_QUERYBUF, &buf_cap) < 0) {
        perror("Помилка QUERYBUF CAPTURE");
        munmap(src_buf.start, src_buf.length);
        close(fd);
        return EXIT_FAILURE;
    }

    struct buffer_info dst_buf;
    dst_buf.length = buf_cap.length;
    dst_buf.start = mmap(NULL, buf_cap.length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, buf_cap.m.offset);
    if (dst_buf.start == MAP_FAILED) {
        perror("Помилка mmap CAPTURE");
        munmap(src_buf.start, src_buf.length);
        close(fd);
        return EXIT_FAILURE;
    }

    /* 5. Заповнення вхідного буфера тестовим шаблоном (сірий колір) */
    memset(src_buf.start, 0x80, src_buf.length);
    buf_out.bytesused = src_buf.length;
    if (xioctl(fd, VIDIOC_QBUF, &buf_out) < 0) {
        perror("Помилка QBUF OUTPUT");
        goto cleanup;
    }

    /* 6. Постановка порожнього буфера в CAPTURE */
    if (xioctl(fd, VIDIOC_QBUF, &buf_cap) < 0) {
        perror("Помилка QBUF CAPTURE");
        goto cleanup;
    }

    /* 7. Запуск потоків */
    enum v4l2_buf_type type_out = V4L2_BUF_TYPE_VIDEO_OUTPUT;
    enum v4l2_buf_type type_cap = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    if (xioctl(fd, VIDIOC_STREAMON, &type_out) < 0 || xioctl(fd, VIDIOC_STREAMON, &type_cap) < 0) {
        perror("Помилка STREAMON");
        goto cleanup;
    }

    /* 8. Очікування виконання через poll() */
    struct pollfd pfd;
    pfd.fd = fd;
    pfd.events = POLLIN;
    int ret = poll(&pfd, 1, 2000); /* тайм-аут 2000 мс */
    if (ret <= 0) {
        fprintf(stderr, "Тайм-аут або збій апаратного прискорювача\n");
        goto cleanup;
    }

    /* 9. Вилучення готових буферів */
    if (xioctl(fd, VIDIOC_DQBUF, &buf_cap) < 0) {
        perror("Помилка DQBUF CAPTURE");
        goto cleanup;
    }
    printf("Кадр успішно оброблено! Отримано %u байтів у форматі NV12 640x480\n", buf_cap.bytesused);

    if (xioctl(fd, VIDIOC_DQBUF, &buf_out) < 0) {
        perror("Помилка DQBUF OUTPUT");
    }

cleanup:
    xioctl(fd, VIDIOC_STREAMOFF, &type_out);
    xioctl(fd, VIDIOC_STREAMOFF, &type_cap);
    munmap(src_buf.start, src_buf.length);
    munmap(dst_buf.start, dst_buf.length);
    close(fd);
    return EXIT_SUCCESS;
}
