/* Прив'язка елементів керування до запиту */
struct v4l2_ext_controls ctrls = {
    .which = V4L2_CTRL_WHICH_REQUEST_VAL,
    .request_fd = req_fd,
    /* список структур SPS, PPS, Slice Params */
};
ioctl(video_fd, VIDIOC_S_EXT_CTRLS, &ctrls);

/* Прив'язка буфера даних слайса до того самого запиту */
struct v4l2_buffer buf = {
    .type = V4L2_BUF_TYPE_VIDEO_OUTPUT,
    .flags = V4L2_BUF_FLAG_REQUEST_FD,
    .request_fd = req_fd,
};
ioctl(video_fd, VIDIOC_QBUF, &buf);

/* Атомарна постановка запиту в чергу виконання */
ioctl(req_fd, MEDIA_REQUEST_IOC_QUEUE, NULL);
