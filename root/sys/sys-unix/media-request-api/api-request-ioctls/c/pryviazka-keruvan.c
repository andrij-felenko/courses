#define V4L2_CTRL_WHICH_CUR_VAL      0
#define V4L2_CTRL_WHICH_DEF_VAL      0x0f000000
#define V4L2_CTRL_WHICH_REQUEST_VAL  0x0f010000

struct v4l2_ext_controls {
    union { __u32 ctrl_class; __u32 which; };
    __u32 count;
    __u32 error_idx;                  /* заповнює драйвер: індекс керування, що не пройшло */
    __s32 request_fd;                 /* дійсне лише при which = REQUEST_VAL */
    __u32 reserved[1];
    struct v4l2_ext_control *controls;
};
