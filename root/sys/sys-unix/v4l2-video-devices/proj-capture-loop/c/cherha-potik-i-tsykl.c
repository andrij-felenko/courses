for (unsigned i = 0; i < req.count; i++) {           /* УСІ буфери — драйверові */
    struct v4l2_buffer b;
    memset(&b, 0, sizeof b);
    b.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    b.memory = V4L2_MEMORY_MMAP;
    b.index  = i;
    if (xioctl(fd, VIDIOC_QBUF, &b) == -1) FAIL("VIDIOC_QBUF");
}

enum v4l2_buf_type type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
if (xioctl(fd, VIDIOC_STREAMON, &type) == -1) FAIL("VIDIOC_STREAMON");

unsigned seen = 0;
while (seen < SKIP + 1) {
    struct pollfd pfd = { .fd = fd, .events = POLLIN };

    int pr = poll(&pfd, 1, 2000);
    if (pr == -1) { if (errno == EINTR) continue; FAIL("poll"); }
    if (pr ==  0) { fputs("дві секунди без кадру\n", stderr); break; }

    struct v4l2_buffer b;
    memset(&b, 0, sizeof b);
    b.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    b.memory = V4L2_MEMORY_MMAP;
    if (xioctl(fd, VIDIOC_DQBUF, &b) == -1) {
        if (errno == EAGAIN) continue;               /* готовність збрехала */
        FAIL("VIDIOC_DQBUF");
    }

    if (b.flags & V4L2_BUF_FLAG_ERROR)
        fputs("кадр пошкоджений, пропускаємо\n", stderr);
    else if (++seen > SKIP)
        save_raw("frame.raw", bufs[b.index].start, STRIDE, ROW, H);

    if (xioctl(fd, VIDIOC_QBUF, &b) == -1) FAIL("VIDIOC_QBUF");  /* назад — завжди */
}
