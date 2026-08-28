#include <linux/v4l2-subdev.h>
#include <sys/ioctl.h>
#include <string.h>

struct v4l2_subdev_selection sel;
memset(&sel, 0, sizeof(sel));

sel.which = V4L2_SUBDEV_FORMAT_ACTIVE;
sel.pad = 0; /* Sink pad */
sel.target = V4L2_SEL_TGT_CROP;
sel.flags = V4L2_SEL_FLAG_LE; /* Менше або дорівнює вихідній області */
sel.r.left = 0;
sel.r.top = 0;
sel.r.width = 1920;
sel.r.height = 1080;

if (ioctl(subdev_fd, VIDIOC_SUBDEV_S_SELECTION, &sel) < 0) {
    /* Обробка помилки прямокутника вибору */
}
