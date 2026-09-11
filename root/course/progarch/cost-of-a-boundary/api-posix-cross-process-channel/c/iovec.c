#include <sys/socket.h>
#include <string.h>

void prepare_single_fd_message(struct msghdr *msg, struct iovec *iov, char *data_byte) {
    // Об'єднання гарантує, що буфер вирівняно під вимоги struct cmsghdr
    static union {
        char   buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } control_storage;

    memset(msg, 0, sizeof(*msg));
    memset(&control_storage, 0, sizeof(control_storage));

    // Обов'язковий вектор корисних даних мінімум на 1 байт
    *data_byte = 'S';
    iov->iov_base = data_byte;
    iov->iov_len = 1;

    msg->msg_iov = iov;
    msg->msg_iovlen = 1;
    msg->msg_control = control_storage.buf;
    msg->msg_controllen = sizeof(control_storage.buf);
}
