#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>

struct v4l2_format mp_fmt;
memset(&mp_fmt, 0, sizeof(mp_fmt));
mp_fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
mp_fmt.fmt.pix_mp.width = 1920;
mp_fmt.fmt.pix_mp.height = 1080;
mp_fmt.fmt.pix_mp.pixelformat = V4L2_PIX_FMT_NV12;
mp_fmt.fmt.pix_mp.field = V4L2_FIELD_NONE;
mp_fmt.fmt.pix_mp.num_planes = 2;

if (ioctl(video_fd, VIDIOC_S_FMT, &mp_fmt) < 0) {
    /* Обробка помилки multi-planar формату */
}
