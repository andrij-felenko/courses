#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_capability cap{};
if (::ioctl(video_fd, VIDIOC_QUERYCAP, &cap) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_QUERYCAP failed");
}

v4l2_format fmt{};
fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
fmt.fmt.pix.width = 1920;
fmt.fmt.pix.height = 1080;
fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
fmt.fmt.pix.field = V4L2_FIELD_NONE;

if (::ioctl(video_fd, VIDIOC_S_FMT, &fmt) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_S_FMT failed");
}
