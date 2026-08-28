/* Налаштування формату на вихідному контакті сенсора через субпристрій V4L2 */
struct v4l2_subdev_format fmt;
memset(&fmt, 0, sizeof(fmt));
fmt.pad = 0; /* Вихідний Pad 0 сенсора */
fmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
fmt.format.width = 1920;
fmt.format.height = 1080;
fmt.format.code = MEDIA_BUS_FMT_SRGGB10_1X10; /* RAW10 Bayer */

if (ioctl(subdev_fd, VIDIOC_SUBDEV_S_FMT, &fmt) < 0) {
    perror("VIDIOC_SUBDEV_S_FMT failed");
}
