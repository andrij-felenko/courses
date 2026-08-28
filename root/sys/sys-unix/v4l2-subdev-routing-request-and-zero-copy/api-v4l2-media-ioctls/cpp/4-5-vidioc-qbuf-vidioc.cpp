#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_buffer buf{};
buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
buf.memory = V4L2_MEMORY_MMAP;
buf.index = 0;

if (::ioctl(video_fd, VIDIOC_QBUF, &buf) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_QBUF failed");
}

v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
if (::ioctl(video_fd, VIDIOC_STREAMON, &type) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_STREAMON failed");
}

v4l2_buffer dqbuf{};
dqbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
dqbuf.memory = V4L2_MEMORY_MMAP;

if (::ioctl(video_fd, VIDIOC_DQBUF, &dqbuf) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_DQBUF failed");
}

uint32_t frame_seq = dqbuf.sequence;
uint32_t payload_bytes = dqbuf.bytesused;

::ioctl(video_fd, VIDIOC_STREAMOFF, &type);
