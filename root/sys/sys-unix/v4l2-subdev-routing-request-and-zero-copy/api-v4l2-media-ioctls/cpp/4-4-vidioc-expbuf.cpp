#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <system_error>

v4l2_exportbuffer exp{};
exp.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
exp.index = 0; // Перший буфер
exp.flags = O_CLOEXEC | O_RDWR;

if (::ioctl(video_fd, VIDIOC_EXPBUF, &exp) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_EXPBUF failed");
}
int dmabuf_fd = exp.fd;
