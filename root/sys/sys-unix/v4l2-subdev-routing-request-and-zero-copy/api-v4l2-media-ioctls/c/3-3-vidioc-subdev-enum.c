#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <stdio.h>
#include <string.h>

struct v4l2_subdev_mbus_code_enum code_enum;
memset(&code_enum, 0, sizeof(code_enum));
code_enum.pad = 0;
code_enum.which = V4L2_SUBDEV_FORMAT_ACTIVE;

while (ioctl(subdev_fd, VIDIOC_SUBDEV_ENUM_MBUS_CODE, &code_enum) == 0) {
    printf("Supported mbus code[%u]: 0x%04x\n", code_enum.index, code_enum.code);
    code_enum.index++;
}
