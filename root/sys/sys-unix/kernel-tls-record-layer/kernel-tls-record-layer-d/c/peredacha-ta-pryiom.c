#include <sys/socket.h>
#include <linux/tls.h>
#include <string.h>
#include <stdio.h>

/* Відправка керуючого запису TLS Alert (тип 21) через kTLS */
ssize_t send_tls_alert(int sockfd, uint8_t alert_code) {
    struct msghdr msg = {0};
    struct iovec iov;
    char cmsg_buf[CMSG_SPACE(sizeof(uint8_t))];

    /* Корисне навантаження Alert (1 байт коду) */
    iov.iov_base = &alert_code;
    iov.iov_len = sizeof(alert_code);

    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cmsg_buf;
    msg.msg_controllen = sizeof(cmsg_buf);

    /* Заповнення допоміжного заголовка cmsg */
    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_TLS;
    cmsg->cmsg_type = TLS_SET_RECORD_TYPE;
    cmsg->cmsg_len = CMSG_LEN(sizeof(uint8_t));
    
    /* Тип запису TLS Alert = 21 (0x15) */
    *((uint8_t *)CMSG_DATA(cmsg)) = 21;

    return sendmsg(sockfd, &msg, 0);
}
