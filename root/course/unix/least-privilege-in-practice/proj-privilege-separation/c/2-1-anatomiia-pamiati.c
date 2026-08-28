#define _GNU_SOURCE
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

/* Відправка файлового дескриптора через Unix Domain сокет */
int send_fd(int socket_fd, int fd_to_send) {
    struct msghdr msg = {0};
    struct iovec iov[1];
    char dummy_char = 'F'; /* Обов'язковий 1 байт корисних даних для протоколу */
    
    /* Буфер для збереження заголовка cmsghdr та самого int дескриптора */
    char cmsg_buf[CMSG_SPACE(sizeof(int))];
    memset(cmsg_buf, 0, sizeof(cmsg_buf));

    iov[0].iov_base = &dummy_char;
    iov[0].iov_len = sizeof(dummy_char);
    msg.msg_iov = iov;
    msg.msg_iovlen = 1;

    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));

    /* Копіюємо числовий дескриптор у область даних cmsghdr */
    memcpy(CMSG_DATA(cmsg), &fd_to_send, sizeof(int));

    if (sendmsg(socket_fd, &msg, 0) < 0) {
        perror("sendmsg SCM_RIGHTS");
        return -1;
    }
    return 0;
}

/* Отримання переданого дескриптора з Unix Domain сокета */
int recv_fd(int socket_fd) {
    struct msghdr msg = {0};
    struct iovec iov[1];
    char dummy_char = 0;
    char cmsg_buf[CMSG_SPACE(sizeof(int))];
    memset(cmsg_buf, 0, sizeof(cmsg_buf));

    iov[0].iov_base = &dummy_char;
    iov[0].iov_len = sizeof(dummy_char);
    msg.msg_iov = iov;
    msg.msg_iovlen = 1;

    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    ssize_t bytes_read = recvmsg(socket_fd, &msg, 0);
    if (bytes_read <= 0) {
        return -1; /* З'єднання закрито або сталася помилка */
    }

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    if (cmsg == NULL || cmsg->cmsg_level != SOL_SOCKET || cmsg->cmsg_type != SCM_RIGHTS) {
        fprintf(stderr, "Помилка: отримано повідомлення без блоку SCM_RIGHTS\n");
        return -1;
    }

    int received_fd = -1;
    memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
    return received_fd;
}
