#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <iostream>
#include <vector>

std::vector<uint32_t> mbus_codes;
v4l2_subdev_mbus_code_enum code_enum{};
code_enum.pad = 0;
code_enum.which = V4L2_SUBDEV_FORMAT_ACTIVE;

while (::ioctl(subdev_fd, VIDIOC_SUBDEV_ENUM_MBUS_CODE, &code_enum) == 0) {
    mbus_codes.push_back(code_enum.code);
    code_enum.index++;
}
