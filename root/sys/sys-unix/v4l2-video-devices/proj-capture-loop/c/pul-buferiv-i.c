enum { WANT = 4, MAXBUF = 8, SKIP = 10 };

struct v4l2_requestbuffers req;
memset(&req, 0, sizeof req);
req.count  = WANT;
req.type   = V4L2_BUF_TYPE_VIDEO_CAPTURE;
req.memory = V4L2_MEMORY_MMAP;
if (xioctl(fd, VIDIOC_REQBUFS, &req) == -1) FAIL("VIDIOC_REQBUFS");

if (req.count < 2 || req.count > MAXBUF) {
    fprintf(stderr, "драйвер дав %u буферів — не наш випадок\n", req.count);
    return 1;
}

struct { void *start; size_t len; } bufs[MAXBUF];

for (unsigned i = 0; i < req.count; i++) {
    struct v4l2_buffer b;
    memset(&b, 0, sizeof b);
    b.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    b.memory = V4L2_MEMORY_MMAP;
    b.index  = i;
    if (xioctl(fd, VIDIOC_QUERYBUF, &b) == -1) FAIL("VIDIOC_QUERYBUF");

    bufs[i].len   = b.length;
    bufs[i].start = mmap(NULL, b.length, PROT_READ | PROT_WRITE,
                         MAP_SHARED, fd, b.m.offset);
    if (bufs[i].start == MAP_FAILED) FAIL("mmap");
}
