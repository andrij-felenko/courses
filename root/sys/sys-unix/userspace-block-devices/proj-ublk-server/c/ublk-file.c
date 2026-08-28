/* ublk-file.c — блоковий пристрій, за яким стоїть звичайний файл.
 *   cc -O2 -o ublk-file ublk-file.c -luring
 *   sudo modprobe ublk_drv && sudo ./ublk-file /srv/backing.img          */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <linux/ublk_cmd.h>
#include <liburing.h>

#define QDEPTH     64                /* тегів у черзі — стільки запитів у польоті */
#define IO_BUF_SZ  (256u * 1024)     /* стеля одного запиту */
#define LOG_BS     4096u             /* логічний блок пристрою */

static struct io_uring ctrl_ring, io_ring;
static struct ublksrv_ctrl_dev_info info;
static const struct ublksrv_io_desc *desc;      /* спільна ділянка описів */
static char *buf[QDEPTH];                       /* по буферу на кожен тег */
static int ctrl_fd, cdev_fd, backing_fd;
static volatile sig_atomic_t stopping;

/* Одна керуюча команда: заповнити структуру, подати, дочекатися відповіді. */
static int ctrl_cmd(__u32 cmd_op, void *payload, __u16 len, __u64 data0)
{
        struct io_uring_sqe *sqe = io_uring_get_sqe(&ctrl_ring);
        struct ublksrv_ctrl_cmd *c;
        struct io_uring_cqe *cqe;
        int ret;

        memset(sqe, 0, 128);                    /* елемент тут 128-байтовий */
        sqe->opcode = IORING_OP_URING_CMD;
        sqe->fd     = ctrl_fd;
        sqe->cmd_op = cmd_op;

        c = (struct ublksrv_ctrl_cmd *)sqe->cmd;
        c->dev_id   = info.dev_id;
        c->queue_id = (__u16)-1;                /* команда не про окрему чергу */
        c->addr     = (__u64)(uintptr_t)payload;
        c->len      = len;
        c->data[0]  = data0;

        if (io_uring_submit(&ctrl_ring) < 0 ||
            io_uring_wait_cqe(&ctrl_ring, &cqe) < 0)
                return -EIO;
        ret = cqe->res;                         /* від'ємне — це −errno драйвера */
        io_uring_cqe_seen(&ctrl_ring, cqe);
        return ret;
}
