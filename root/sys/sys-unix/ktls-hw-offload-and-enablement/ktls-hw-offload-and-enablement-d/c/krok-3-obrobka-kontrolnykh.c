/* Приклад на C: Відправка TLS Alert (close_notify) */
#include <sys/socket.h>
#include <linux/tls.h>

void send_tls_close_notify(int sock_fd) {
    char alert_payload[2] = {1, 0}; /* close_notify alert */
    struct iovec iov = { .iov_base = alert_payload, .iov_len = sizeof(alert_payload) };
    
    char cmsgbuf[CMSG_SPACE(sizeof(unsigned char))];
    struct msghdr msg = {0};
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cmsgbuf;
    msg.msg_controllen = sizeof(cmsgbuf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_TLS;
    cmsg->cmsg_type = TLS_SET_RECORD_TYPE;
    cmsg->cmsg_len = CMSG_LEN(sizeof(unsigned char));
    *((unsigned char *)CMSG_DATA(cmsg)) = 21; /* Тип 21 = TLS Alert */

    sendmsg(sock_fd, &msg, 0);
}
