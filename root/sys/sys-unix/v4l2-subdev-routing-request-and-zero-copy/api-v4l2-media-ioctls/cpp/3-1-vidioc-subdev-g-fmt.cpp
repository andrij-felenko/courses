#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_subdev_format subfmt{};
subfmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
subfmt.pad = 0; // Source pad
subfmt.format.width = 1920;
subfmt.format.height = 1080;
subfmt.format.code = MEDIA_BUS_FMT_SBGGR10_1X10; // 10-bit Bayer RAW
subfmt.format.field = V4L2_FIELD_NONE;
subfmt.format.colorspace = V4L2_COLORSPACE_RAW;

if (::ioctl(subdev_fd, VIDIOC_SUBDEV_S_FMT, &subfmt) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_SUBDEV_S_FMT failed");
}
