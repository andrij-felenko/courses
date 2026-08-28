#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <string.h>

struct v4l2_exportbuffer exp;
memset(&exp, 0, sizeof(exp));
exp.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
exp.index = 0; /* Перший буфер */
exp.flags = O_CLOEXEC | O_RDWR;

if (ioctl(video_fd, VIDIOC_EXPBUF, &exp) == 0) {
    int dmabuf_fd = exp.fd; /* Дескриптор для передачі в DRM або GPU */
}
