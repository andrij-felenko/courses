struct io_uring ctrl;
io_uring_queue_init(2, &ctrl, IORING_SETUP_SQE128);   /* 32 байти не влізуть у звичайний SQE */
int cfd = open("/dev/ublk-control", O_RDWR);

struct ublksrv_ctrl_dev_info info = {
        .nr_hw_queues     = 1,
        .queue_depth      = 128,
        .max_io_buf_bytes = 512 * 1024,
        .dev_id           = (__u32)-1,        /* хай ядро вибере номер */
        .flags            = UBLK_F_CMD_IOCTL_ENCODE,
};

struct io_uring_sqe *sqe = io_uring_get_sqe(&ctrl);
io_uring_prep_read(sqe, cfd, NULL, 0, 0);             /* обнуляємо поля, далі перекриваємо */
sqe->opcode = IORING_OP_URING_CMD;
sqe->cmd_op = UBLK_U_CMD_ADD_DEV;

struct ublksrv_ctrl_cmd *c = (struct ublksrv_ctrl_cmd *)sqe->cmd;
c->dev_id   = (__u32)-1;
c->queue_id = (__u16)-1;                              /* команда не про чергу */
c->addr     = (__u64)(uintptr_t)&info;
c->len      = sizeof(info);

io_uring_submit(&ctrl);

struct io_uring_cqe *cqe;
io_uring_wait_cqe(&ctrl, &cqe);
if (cqe->res == 0)
        printf("з'явився /dev/ublkc%u\n", info.dev_id);   /* номер уписало ядро */
