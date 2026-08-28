#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <unistd.h>

static void die(const char *what) { perror(what); _exit(1); }

/* Надсилає один дескриптор разом з одним байтом звичайних даних. */
static int send_fd(int sock, int fd)
{
    char byte = '.';                        /* хоча б один справжній байт */
    struct iovec iov = { .iov_base = &byte, .iov_len = 1 };

    union {                                 /* union дає буферу потрібне вирівнювання */
        char buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } u;
    memset(&u, 0, sizeof(u));

    struct msghdr msg = {
        .msg_iov        = &iov,
        .msg_iovlen     = 1,
        .msg_control    = u.buf,
        .msg_controllen = sizeof(u.buf),    /* тобто CMSG_SPACE(sizeof(int)) */
    };

    struct cmsghdr *cm = CMSG_FIRSTHDR(&msg);
    cm->cmsg_level = SOL_SOCKET;
    cm->cmsg_type  = SCM_RIGHTS;
    cm->cmsg_len   = CMSG_LEN(sizeof(int)); /* саме LEN, а не SPACE */
    memcpy(CMSG_DATA(cm), &fd, sizeof(int));/* memcpy, бо вказівник може бути невирівняний */

    ssize_t n;
    do { n = sendmsg(sock, &msg, 0); } while (n < 0 && errno == EINTR);
    return n == 1 ? 0 : -1;
}
