struct v4l2_exportbuffer expbuf;
int plane_fds[2];

for (int p = 0; p < 2; ++p) {
    memset(&expbuf, 0, sizeof(expbuf));
    expbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    expbuf.index = buffer_index;
    expbuf.plane = p; /* 0 for Y, 1 for UV */
    expbuf.flags = O_CLOEXEC | O_RDWR;
    
    if (ioctl(video_fd, VIDIOC_EXPBUF, &expbuf) == 0) {
        plane_fds[p] = expbuf.fd;
    }
}
