int fd = open("/dev/video0", O_RDWR | O_NONBLOCK);
if (fd < 0)
    return -1;

struct v4l2_capability cap;
memset(&cap, 0, sizeof cap);
if (ioctl(fd, VIDIOC_QUERYCAP, &cap) < 0)
    return -1;

__u32 caps = (cap.capabilities & V4L2_CAP_DEVICE_CAPS)
           ? cap.device_caps : cap.capabilities;

int mplane = !!(caps & V4L2_CAP_VIDEO_M2M_MPLANE);
int splane = !!(caps & V4L2_CAP_VIDEO_M2M);
if (!(mplane || splane) || !(caps & V4L2_CAP_STREAMING))
    return -1;                       /* це не декодер пам'ять-у-пам'ять */
