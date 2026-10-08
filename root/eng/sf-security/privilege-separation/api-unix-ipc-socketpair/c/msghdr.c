#include <sys/socket.h>
#include <sys/types.h>
#include <string.h>
#include <unistd.h>

int send_fd(int socket, int fd_to_send) {
    struct msghdr msg = {0};
    char buf[1] = {0}; // Принаймні 1 байт звичайних даних для POSIX-сумісності
    struct iovec io = { .iov_base = buf, .iov_len = sizeof(buf) };

    union {
        char buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } cmsgu;

    msg.msg_iov = &io;
    msg.msg_iovlen = 1;
    msg.msg_control = cmsgu.buf;
    msg.msg_controllen = sizeof(cmsgu.buf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));

    memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

    if (sendmsg(socket, &msg, 0) < 0) {
        return -1;
    }
    return 0;
}
