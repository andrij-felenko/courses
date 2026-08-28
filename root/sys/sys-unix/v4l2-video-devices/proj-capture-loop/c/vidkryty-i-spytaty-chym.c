int fd = open("/dev/video0", O_RDWR | O_NONBLOCK);
if (fd == -1) FAIL("open /dev/video0");

struct v4l2_capability cap;
if (xioctl(fd, VIDIOC_QUERYCAP, &cap) == -1) FAIL("VIDIOC_QUERYCAP");

unsigned caps = (cap.capabilities & V4L2_CAP_DEVICE_CAPS)
              ? cap.device_caps : cap.capabilities;

if (!(caps & V4L2_CAP_VIDEO_CAPTURE)) { fputs("вузол не знімає відео\n",  stderr); return 1; }
if (!(caps & V4L2_CAP_STREAMING))     { fputs("немає черги буферів\n",    stderr); return 1; }
