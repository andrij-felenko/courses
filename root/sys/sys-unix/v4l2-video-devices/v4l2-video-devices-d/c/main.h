struct v4l2_format fmt = { .type = V4L2_BUF_TYPE_VIDEO_CAPTURE };
fmt.fmt.pix.width       = 1366;
fmt.fmt.pix.height      = 768;
fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_NV12;
fmt.fmt.pix.field       = V4L2_FIELD_NONE;
ioctl(fd, VIDIOC_S_FMT, &fmt);

/* читаємо, що вийшло насправді */
printf("%ux%u, крок рядка %u Б, кадр %u Б\n",
       fmt.fmt.pix.width, fmt.fmt.pix.height,
       fmt.fmt.pix.bytesperline, fmt.fmt.pix.sizeimage);
