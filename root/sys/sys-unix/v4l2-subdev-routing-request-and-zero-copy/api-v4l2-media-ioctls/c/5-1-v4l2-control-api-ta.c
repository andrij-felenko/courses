#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>

struct v4l2_ext_control ext_ctrls[2];
memset(ext_ctrls, 0, sizeof(ext_ctrls));

ext_ctrls[0].id = V4L2_CID_EXPOSURE;
ext_ctrls[0].value = 250;

ext_ctrls[1].id = V4L2_CID_ANALOGUE_GAIN;
ext_ctrls[1].value = 16;

struct v4l2_ext_controls ctrls;
memset(&ctrls, 0, sizeof(ctrls));
ctrls.ctrl_class = V4L2_CTRL_CLASS_USER;
ctrls.count = 2;
ctrls.controls = ext_ctrls;

if (ioctl(video_fd, VIDIOC_S_EXT_CTRLS, &ctrls) < 0) {
    /* Обробка помилки атомарного встановлення кластера контролів */
}
