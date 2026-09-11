#define _GNU_SOURCE
#include <sys/socket.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>

// Безпечна передача дескриптора через сокетний канал
int send_fd(int channel_fd, int fd_to_send) {
    struct msghdr msg;
    struct iovec iov;
    char dummy_byte = 'D';

    // Вирівняний буфер під одне керуюче повідомлення
    union {
        char buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } u;

    memset(&msg, 0, sizeof(msg));
    memset(&u, 0, sizeof(u));

    // Обов'язковий вектор корисних даних
    iov.iov_base = &dummy_byte;
    iov.iov_len = sizeof(dummy_byte);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    // Налаштовуємо буфер керування
    msg.msg_control = u.buf;
    msg.msg_controllen = sizeof(u.buf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));

    // Записуємо дескриптор у корисну область блоку керування
    memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

    if (sendmsg(channel_fd, &msg, 0) == -1) {
        return -1;
    }

    return 0;
}

// Безпечне отримання дескриптора з перевіркою MSG_CTRUNC
int recv_fd(int channel_fd) {
    struct msghdr msg;
    struct iovec iov;
    char dummy_byte;

    union {
        char buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } u;

    memset(&msg, 0, sizeof(msg));
    memset(&u, 0, sizeof(u));

    iov.iov_base = &dummy_byte;
    iov.iov_len = sizeof(dummy_byte);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

    msg.msg_control = u.buf;
    msg.msg_controllen = sizeof(u.buf);

    ssize_t n = recvmsg(channel_fd, &msg, 0);
    if (n <= 0) {
        return -1; // Канал закрито або сталася помилка
    }

    // Захист від прихованого витоку ресурсів ядра
    if (msg.msg_flags & MSG_CTRUNC) {
        errno = EMSGSIZE;
        return -1;
    }

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    if (!cmsg || cmsg->cmsg_level != SOL_SOCKET || cmsg->cmsg_type != SCM_RIGHTS) {
        errno = EPROTO;
        return -1;
    }

    int received_fd = -1;
    memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
    return received_fd;
}
