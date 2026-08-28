#define VIDIOC_SUBDEV_ENUM_MBUS_CODE  _IOWR('V',  2, struct v4l2_subdev_mbus_code_enum)
#define VIDIOC_SUBDEV_G_FMT           _IOWR('V',  4, struct v4l2_subdev_format)
#define VIDIOC_SUBDEV_S_FMT           _IOWR('V',  5, struct v4l2_subdev_format)
#define VIDIOC_SUBDEV_G_SELECTION     _IOWR('V', 61, struct v4l2_subdev_selection)
#define VIDIOC_SUBDEV_S_SELECTION     _IOWR('V', 62, struct v4l2_subdev_selection)
#define VIDIOC_SUBDEV_ENUM_FRAME_SIZE _IOWR('V', 74, struct v4l2_subdev_frame_size_enum)

struct v4l2_subdev_format {
        __u32 which;                       /* TRY або ACTIVE */
        __u32 pad;
        struct v4l2_mbus_framefmt format;  /* width, height, code, field,
                                              colorspace, ycbcr_enc,
                                              quantization, xfer_func */
        __u32 stream;                      /* 6.3: номер потоку в паді */
        __u32 reserved[7];
};

struct v4l2_subdev_selection {
        __u32 which; __u32 pad; __u32 target; __u32 flags;
        struct v4l2_rect r;                /* left, top, width, height */
        __u32 stream; __u32 reserved[7];
};

struct v4l2_subdev_mbus_code_enum {
        __u32 pad; __u32 index; __u32 code; __u32 which;
        __u32 flags; __u32 stream; __u32 reserved[6];
};

struct v4l2_subdev_frame_size_enum {
        __u32 index; __u32 pad; __u32 code;
        __u32 min_width, max_width, min_height, max_height;
        __u32 which; __u32 stream; __u32 reserved[7];
};

enum v4l2_subdev_format_whence {
        V4L2_SUBDEV_FORMAT_TRY    = 0,
        V4L2_SUBDEV_FORMAT_ACTIVE = 1,
};
