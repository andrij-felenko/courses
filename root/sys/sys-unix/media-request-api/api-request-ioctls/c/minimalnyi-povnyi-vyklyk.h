/* 1. чи має ця черга право приймати буфери в запитах */
struct v4l2_requestbuffers rb = {
    .count = 0, .type = V4L2_BUF_TYPE_VIDEO_CAPTURE, .memory = V4L2_MEMORY_MMAP,
};
ioctl(video_fd, VIDIOC_REQBUFS, &rb);
if (!(rb.capabilities & V4L2_BUF_CAP_SUPPORTS_REQUESTS))
    return -1;

/* 2. запит живе на медіапристрої */
int req_fd;
if (ioctl(media_fd, MEDIA_IOC_REQUEST_ALLOC, &req_fd) < 0)
    return -1;                                   /* ENOTTY */

/* 3. наповнення: керування — на вузлі сенсора, буфер — на відеовузлі */
struct v4l2_ext_control c = { .id = V4L2_CID_EXPOSURE_ABSOLUTE, .value = 120 };
struct v4l2_ext_controls ctrls = {
    .which = V4L2_CTRL_WHICH_REQUEST_VAL, .request_fd = req_fd,
    .count = 1, .controls = &c,
};
ioctl(subdev_fd, VIDIOC_S_EXT_CTRLS, &ctrls);    /* EBUSY, якщо запит уже в черзі */

struct v4l2_buffer buf = {                       /* занулення обов'язкове */
    .type = V4L2_BUF_TYPE_VIDEO_CAPTURE, .memory = V4L2_MEMORY_MMAP, .index = 0,
    .flags = V4L2_BUF_FLAG_REQUEST_FD, .request_fd = req_fd,
};
ioctl(video_fd, VIDIOC_QBUF, &buf);              /* EBADR / EINVAL / EBUSY */

/* 4. пуск і очікування */
ioctl(req_fd, MEDIA_REQUEST_IOC_QUEUE, NULL);    /* ENOENT, якщо буфера немає */
struct pollfd p = { .fd = req_fd, .events = POLLPRI };
poll(&p, 1, -1);

/* 5. що драйвер справді застосував (до завершення — EACCES) */
ioctl(subdev_fd, VIDIOC_G_EXT_CTRLS, &ctrls);
ioctl(video_fd, VIDIOC_DQBUF, &buf);

/* 6. той самий дескриптор — на наступний кадр */
ioctl(req_fd, MEDIA_REQUEST_IOC_REINIT, NULL);
