#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>
#include <stdio.h>

struct v4l2_capability cap;
memset(&cap, 0, sizeof(cap));
if (ioctl(video_fd, VIDIOC_QUERYCAP, &cap) < 0) {
    perror("VIDIOC_QUERYCAP failed");
    return -1;
}

struct v4l2_format fmt;
memset(&fmt, 0, sizeof(fmt));
fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
fmt.fmt.pix.width = 1920;
fmt.fmt.pix.height = 1080;
fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_UYVY;
fmt.fmt.pix.field = V4L2_FIELD_NONE;

if (ioctl(video_fd, VIDIOC_S_FMT, &fmt) < 0) {
    perror("VIDIOC_S_FMT failed");
    return -1;
}
