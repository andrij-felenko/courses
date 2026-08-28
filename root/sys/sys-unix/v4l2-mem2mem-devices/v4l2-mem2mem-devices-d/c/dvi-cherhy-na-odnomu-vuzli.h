/* Налаштування формату вхідного потоку (OUTPUT): сирий YUYV 1920×1080 */
struct v4l2_format fmt_src = {
    .type = V4L2_BUF_TYPE_VIDEO_OUTPUT,
    .fmt.pix.width = 1920,
    .fmt.pix.height = 1080,
    .fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV,
};
ioctl(fd, VIDIOC_S_FMT, &fmt_src);

/* Налаштування формату вихідного потоку (CAPTURE): стиснений H.264 */
struct v4l2_format fmt_dst = {
    .type = V4L2_BUF_TYPE_VIDEO_CAPTURE,
    .fmt.pix.pixelformat = V4L2_PIX_FMT_H264,
    .fmt.pix.sizeimage = 2 * 1024 * 1024, /* 2 МБ буфер під бітстрім */
};
ioctl(fd, VIDIOC_S_FMT, &fmt_dst);
