struct v4l2_ext_control c = { .id = V4L2_CID_EXPOSURE_ABSOLUTE, .value = 120 };
struct v4l2_ext_controls ctrls = {
    .which      = V4L2_CTRL_WHICH_REQUEST_VAL,
    .request_fd = req_fd,
    .count      = 1,
    .controls   = &c,
};
ioctl(subdev_fd, VIDIOC_S_EXT_CTRLS, &ctrls);

struct v4l2_buffer buf = {
    .type       = V4L2_BUF_TYPE_VIDEO_CAPTURE,
    .memory     = V4L2_MEMORY_MMAP,
    .index      = 2,
    .flags      = V4L2_BUF_FLAG_REQUEST_FD,
    .request_fd = req_fd,
};
ioctl(video_fd, VIDIOC_QBUF, &buf);

ioctl(req_fd, MEDIA_REQUEST_IOC_QUEUE, NULL);        /* аж тепер щось відбувається */
