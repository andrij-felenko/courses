/* Один прохід stateful-декодера. Обробку помилок скорочено. */
static int decode_step(int fd, struct v4l2_plane *op, struct v4l2_plane *cp)
{
    struct pollfd pfd = { .fd = fd, .events = POLLIN | POLLOUT | POLLPRI };
    if (poll(&pfd, 1, 500) <= 0)
        return 0;

    if (pfd.revents & POLLPRI) {           /* зміна роздільності */
        struct v4l2_event ev;
        memset(&ev, 0, sizeof ev);
        ioctl(fd, VIDIOC_DQEVENT, &ev);
        if (ev.type == V4L2_EVENT_SOURCE_CHANGE &&
            (ev.u.src_change.changes & V4L2_EVENT_SRC_CH_RESOLUTION))
            return RESETUP_CAPTURE;
    }

    if (pfd.revents & POLLOUT) {           /* звільнився вхідний буфер */
        struct v4l2_buffer b;
        memset(&b, 0, sizeof b);
        b.type     = V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE;
        b.memory   = V4L2_MEMORY_MMAP;
        b.m.planes = op;
        b.length   = 1;
        if (ioctl(fd, VIDIOC_DQBUF, &b) == 0)
            refill_and_queue(fd, &b);      /* наступна одиниця доступу */
    }

    if (pfd.revents & POLLIN) {            /* готовий кадр */
        struct v4l2_buffer b;
        memset(&b, 0, sizeof b);
        b.type     = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
        b.memory   = V4L2_MEMORY_MMAP;
        b.m.planes = cp;
        b.length   = 2;                    /* NV12M: дві площини */
        if (ioctl(fd, VIDIOC_DQBUF, &b) < 0)
            return (errno == EPIPE) ? STREAM_END : 0;
        if (b.flags & V4L2_BUF_FLAG_LAST)
            return DRAIN_DONE;
        if (!(b.flags & V4L2_BUF_FLAG_ERROR))
            use_frame(fd, b.index, b.timestamp);
        ioctl(fd, VIDIOC_QBUF, &b);        /* тару — назад у чергу */
    }
    return 0;
}
