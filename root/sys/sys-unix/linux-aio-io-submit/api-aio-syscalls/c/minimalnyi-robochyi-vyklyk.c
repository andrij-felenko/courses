#define _GNU_SOURCE
#include <linux/aio_abi.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdio.h>

int main(void)
{
    aio_context_t ctx = 0;                    /* обов'язково нуль */
    if (syscall(SYS_io_setup, 8, &ctx) < 0) { perror("io_setup"); return 1; }

    int fd = open("/etc/hostname", O_RDONLY);
    char buf[4096];

    struct iocb cb;
    memset(&cb, 0, sizeof cb);                /* резервні поля мусять бути нулем */
    cb.aio_lio_opcode = IOCB_CMD_PREAD;
    cb.aio_fildes     = fd;
    cb.aio_buf        = (unsigned long long) buf;
    cb.aio_nbytes     = sizeof buf;
    cb.aio_offset     = 0;
    cb.aio_data       = 0xC0FFEE;             /* мітка, повернеться незміненою */

    struct iocb *list[1] = { &cb };
    if (syscall(SYS_io_submit, ctx, 1L, list) != 1) { perror("io_submit"); return 1; }

    struct io_event ev;
    if (syscall(SYS_io_getevents, ctx, 1L, 1L, &ev, NULL) != 1) {
        perror("io_getevents"); return 1;
    }
    printf("мітка %llx, res %lld\n",
           (unsigned long long) ev.data, (long long) ev.res);

    syscall(SYS_io_destroy, ctx);
    close(fd);
    return 0;
}
