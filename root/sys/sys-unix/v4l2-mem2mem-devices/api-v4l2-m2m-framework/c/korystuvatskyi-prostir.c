struct v4l2_format fmt = {
    .type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE,
    .fmt.pix_mp = {
        .width = 1920,
        .height = 1080,
        .pixelformat = V4L2_PIX_FMT_NV12M,
        .num_planes = 2,
        .plane_fmt[0] = { .sizeimage = 1920 * 1080, .bytesperline = 1920 },
        .plane_fmt[1] = { .sizeimage = 1920 * 540,  .bytesperline = 1920 },
    },
};
ioctl(fd, VIDIOC_S_FMT, &fmt);
