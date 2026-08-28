// Ідіоматичний еквівалент на C++ для налаштування формату субпристрою
#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <system_error>
#include <cstring>

void configureSubdevFormat(int subdevFd, uint32_t pad, uint32_t width, uint32_t height, uint32_t mbusCode) {
    v4l2_subdev_format fmt{};
    fmt.pad = pad;
    fmt.which = V4L2_SUBDEV_FORMAT_ACTIVE;
    fmt.format.width = width;
    fmt.format.height = height;
    fmt.format.code = mbusCode;

    if (::ioctl(subdevFd, VIDIOC_SUBDEV_S_FMT, &fmt) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка VIDIOC_SUBDEV_S_FMT");
    }
}
