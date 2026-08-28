#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <string.h>

struct v4l2_subdev_format subfmt;
memset(&subfmt, 0, sizeof(subfmt));

subfmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
subfmt.pad = 0; /* Source pad */
subfmt.format.width = 1920;
subfmt.format.height = 1080;
subfmt.format.code = MEDIA_BUS_FMT_SBGGR10_1X10; /* 10-bit Bayer RAW */
subfmt.format.field = V4L2_FIELD_NONE;
subfmt.format.colorspace = V4L2_COLORSPACE_RAW;

if (ioctl(subdev_fd, VIDIOC_SUBDEV_S_FMT, &subfmt) < 0) {
    /* Обробка помилки встановлення формату субпристрою */
}
