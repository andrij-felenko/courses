/* Команда завершення потоку (Drain / EOS) */
#define VIDIOC_DECODER_CMD               _IOWR('V', 96, struct v4l2_decoder_cmd)
#define V4L2_DEC_CMD_STOP                1
#define V4L2_DEC_CMD_START               2
#define V4L2_DEC_CMD_PAUSE               3
#define V4L2_DEC_CMD_RESUME              4
#define V4L2_DEC_CMD_FLUSH               5

/* Подія зміни роздільності потоку (DRC) */
#define V4L2_EVENT_SOURCE_CHANGE         5
#define V4L2_EVENT_SRC_CH_RESOLUTION     (1 << 0)

/* Підписка на подію */
struct v4l2_event_subscription sub = {
    .type = V4L2_EVENT_SOURCE_CHANGE,
};
ioctl(fd, VIDIOC_SUBSCRIBE_EVENT, &sub);
