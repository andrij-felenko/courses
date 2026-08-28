#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <system_error>

v4l2_event_subscription sub{};
sub.type = V4L2_EVENT_SOURCE_CHANGE;

if (::ioctl(video_fd, VIDIOC_SUBSCRIBE_EVENT, &sub) < 0) {
    throw std::system_error(errno, std::generic_category(), "SUBSCRIBE_EVENT failed");
}

v4l2_event ev{};
if (::ioctl(video_fd, VIDIOC_DQEVENT, &ev) == 0) {
    if (ev.type == V4L2_EVENT_SOURCE_CHANGE) {
        // Обробка асинхронної зміни конфігурації
    }
}
