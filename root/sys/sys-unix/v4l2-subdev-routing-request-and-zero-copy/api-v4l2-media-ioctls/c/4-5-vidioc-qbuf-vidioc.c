#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>

/* 1. Постановка буфера в чергу ядра */
struct v4l2_buffer buf;
memset(&buf, 0, sizeof(buf));
buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
buf.memory = V4L2_MEMORY_MMAP;
buf.index = 0;

if (ioctl(video_fd, VIDIOC_QBUF, &buf) < 0) {
    /* Обробка помилки QBUF */
}

/* 2. Запуск відеопотоку */
enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
if (ioctl(video_fd, VIDIOC_STREAMON, &type) < 0) {
    /* Обробка помилки STREAMON */
}

/* 3. Вилучення готового кадру */
struct v4l2_buffer dqbuf;
memset(&dqbuf, 0, sizeof(dqbuf));
dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
dqbuf.memory = V4L2_MEMORY_MMAP;

if (ioctl(video_fd, VIDIOC_DQBUF, &dqbuf) == 0) {
    uint32_t frame_seq = dqbuf.sequence;
    uint32_t payload_bytes = dqbuf.bytesused;
}

/* 4. Зупинка відеопотоку */
ioctl(video_fd, VIDIOC_STREAMOFF, &type);
