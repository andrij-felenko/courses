int fd = open("/dev/video0", O_RDWR | O_NONBLOCK);

struct v4l2_capability cap = {0};
if (ioctl(fd, VIDIOC_QUERYCAP, &cap) < 0) { perror("QUERYCAP"); return -1; }

__u32 caps = (cap.capabilities & V4L2_CAP_DEVICE_CAPS)
           ? cap.device_caps : cap.capabilities;      /* саме цей вузол */
if (!(caps & V4L2_CAP_VIDEO_CAPTURE) || !(caps & V4L2_CAP_STREAMING))
    return fprintf(stderr, "%s: не камера з обміном буферами\n", cap.card), -1;

struct v4l2_fmtdesc f = { .type = V4L2_BUF_TYPE_VIDEO_CAPTURE };
for (f.index = 0; ioctl(fd, VIDIOC_ENUM_FMT, &f) == 0; f.index++) {
    printf("%.4s  %s\n", (char *)&f.pixelformat, f.description);

    struct v4l2_frmsizeenum s = { .pixel_format = f.pixelformat };
    for (s.index = 0; ioctl(fd, VIDIOC_ENUM_FRAMESIZES, &s) == 0; s.index++)
        if (s.type == V4L2_FRMSIZE_TYPE_DISCRETE)
            printf("    %ux%u\n", s.discrete.width, s.discrete.height);
        else
            printf("    %u..%u крок %u\n", s.stepwise.min_width,
                   s.stepwise.max_width, s.stepwise.step_width);
}
if (errno != EINVAL) perror("ENUM_FMT");   /* EINVAL — штатний кінець переліку */
