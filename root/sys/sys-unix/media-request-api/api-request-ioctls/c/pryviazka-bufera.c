/* <linux/videodev2.h> */
#define V4L2_BUF_FLAG_REQUEST_FD            0x00800000
#define V4L2_BUF_FLAG_M2M_HOLD_CAPTURE_BUF  0x00000200

struct v4l2_buffer {
    /* … index, type, bytesused, flags, field, timestamp, … */
    __u32 reserved2;
    union {
        __s32 request_fd;   /* дійсне лише при V4L2_BUF_FLAG_REQUEST_FD */
        __u32 reserved;
    };
};
