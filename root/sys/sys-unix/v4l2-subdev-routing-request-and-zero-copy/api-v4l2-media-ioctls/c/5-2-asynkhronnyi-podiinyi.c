#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <string.h>

/* 1. Підписка на подію зміни джерела (Source Change) */
struct v4l2_event_subscription sub;
memset(&sub, 0, sizeof(sub));
sub.type = V4L2_EVENT_SOURCE_CHANGE;

if (ioctl(video_fd, VIDIOC_SUBSCRIBE_EVENT, &sub) < 0) {
    /* Обробка помилки підписки */
}

/* 2. Отримання події з черги ядра */
struct v4l2_event ev;
memset(&ev, 0, sizeof(ev));
if (ioctl(video_fd, VIDIOC_DQEVENT, &ev) == 0) {
    if (ev.type == V4L2_EVENT_SOURCE_CHANGE) {
        printf("Source resolution change event received!\n");
    }
}
