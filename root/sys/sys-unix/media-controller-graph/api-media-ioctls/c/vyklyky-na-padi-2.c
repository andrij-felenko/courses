struct v4l2_subdev_mbus_code_enum mc = {
        .pad = 0, .index = 0, .which = V4L2_SUBDEV_FORMAT_ACTIVE,
};
while (ioctl(sd, VIDIOC_SUBDEV_ENUM_MBUS_CODE, &mc) == 0) {
        struct v4l2_subdev_frame_size_enum fs = {
                .pad = 0, .index = 0, .code = mc.code,
                .which = V4L2_SUBDEV_FORMAT_ACTIVE,
        };
        while (ioctl(sd, VIDIOC_SUBDEV_ENUM_FRAME_SIZE, &fs) == 0) {
                printf("0x%04x  %ux%u … %ux%u\n", mc.code,
                       fs.min_width, fs.min_height, fs.max_width, fs.max_height);
                fs.index++;
        }
        mc.index++;
}
