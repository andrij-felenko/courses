struct v4l2_format fmt;
memset(&fmt, 0, sizeof fmt);                 /* нулі обов'язкові: ядро судить резервні поля */
fmt.type                = V4L2_BUF_TYPE_VIDEO_CAPTURE;
fmt.fmt.pix.width       = 1366;
fmt.fmt.pix.height      = 768;
fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
fmt.fmt.pix.field       = V4L2_FIELD_NONE;
if (xioctl(fd, VIDIOC_S_FMT, &fmt) == -1) FAIL("VIDIOC_S_FMT");

const unsigned H      = fmt.fmt.pix.height;         /* могло змінитися */
const unsigned STRIDE = fmt.fmt.pix.bytesperline;   /* крок рядка в пам'яті */
const unsigned ROW    = fmt.fmt.pix.width * 2;      /* корисних байтів у рядку, YUYV */
