struct v4l2_subdev_format fmt = {
    .pad   = 0,
    .which = V4L2_SUBDEV_FORMAT_ACTIVE,
    .format = {
        .width  = 1920,
        .height = 1080,
        .code   = MEDIA_BUS_FMT_SGRBG10_1X10,
        .field  = V4L2_FIELD_NONE,
    },
};
ioctl(subdev_fd, VIDIOC_SUBDEV_S_FMT, &fmt);
