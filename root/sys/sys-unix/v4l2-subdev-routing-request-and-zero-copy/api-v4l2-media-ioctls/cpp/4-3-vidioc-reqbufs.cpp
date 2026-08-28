#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_requestbuffers req{};
req.count = 4;
req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
req.memory = V4L2_MEMORY_MMAP;

if (::ioctl(video_fd, VIDIOC_REQBUFS, &req) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_REQBUFS failed");
}
