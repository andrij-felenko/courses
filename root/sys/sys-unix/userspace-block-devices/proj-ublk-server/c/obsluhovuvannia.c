/* Одна команда на тег: озброїти вперше або віддати вердикт і озброїти знову. */
static void arm(unsigned tag, __u32 cmd_op, int result)
{
        struct io_uring_sqe *sqe = io_uring_get_sqe(&io_ring);
        struct ublksrv_io_cmd *c;

        io_uring_prep_rw(IORING_OP_URING_CMD, sqe, cdev_fd, NULL, 0, 0);
        sqe->cmd_op = cmd_op;           /* лежить там само, де off, — тому ПІСЛЯ prep */

        c = (struct ublksrv_io_cmd *)sqe->cmd;
        c->q_id   = 0;
        c->tag    = (__u16)tag;
        c->result = result;
        c->addr   = (__u64)(uintptr_t)buf[tag];
        io_uring_sqe_set_data64(sqe, tag);
}

/* Тут і тільки тут живе «що це за сховище». Решта файлу — обв'язка. */
static int serve(const struct ublksrv_io_desc *iod, char *b)
{
        __u32  op  = iod->op_flags & 0xff;
        off_t  off = (off_t)iod->start_sector * 512;
        size_t len = (size_t)iod->nr_sectors * 512;
        ssize_t n;

        switch (op) {
        case UBLK_IO_OP_READ:
                n = pread(backing_fd, b, len, off);
                return n < 0 ? -errno : (int)n;

        case UBLK_IO_OP_WRITE:
                n = pwrite(backing_fd, b, len, off);
                if (n < 0)
                        return -errno;
                if (iod->op_flags & UBLK_IO_F_FUA)       /* «на носій — до відповіді» */
                        if (fdatasync(backing_fd) < 0)
                                return -errno;
                return (int)n;

        case UBLK_IO_OP_FLUSH:                           /* хтось нагорі покликав fsync */
                return fdatasync(backing_fd) < 0 ? -errno : 0;

        default:
                return -EOPNOTSUPP;
        }
}
