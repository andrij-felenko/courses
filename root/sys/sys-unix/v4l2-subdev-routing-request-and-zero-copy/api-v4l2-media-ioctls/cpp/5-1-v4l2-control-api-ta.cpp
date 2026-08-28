#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <array>
#include <system_error>

std::array<v4l2_ext_control, 2> ext_ctrls{};
ext_ctrls[0].id = V4L2_CID_EXPOSURE;
ext_ctrls[0].value = 250;

ext_ctrls[1].id = V4L2_CID_ANALOGUE_GAIN;
ext_ctrls[1].value = 16;

v4l2_ext_controls ctrls{};
ctrls.ctrl_class = V4L2_CTRL_CLASS_USER;
ctrls.count = static_cast<uint32_t>(ext_ctrls.size());
ctrls.controls = ext_ctrls.data();

if (::ioctl(video_fd, VIDIOC_S_EXT_CTRLS, &ctrls) < 0) {
    throw std::system_error(errno, std::generic_category(), "VIDIOC_S_EXT_CTRLS failed");
}
