#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/sock_diag.h>
#include <linux/inet_diag.h>
#include <arpa/inet.h>

/* Відправка бінарного запиту sock_diag для отримання сокетів TCP у стані LISTEN */
int send_diag_dump_request(int nl_fd) {
    struct {
        struct nlmsghdr nlh;
        struct inet_diag_req_v2 req;
    } msg;

    memset(&msg, 0, sizeof(msg));
    msg.nlh.nlmsg_len = sizeof(msg);
    msg.nlh.nlmsg_type = SOCK_DIAG_BY_FAMILY;
    msg.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_DUMP;
    msg.nlh.nlmsg_seq = 123456;

    msg.req.sdiag_family = AF_INET;
    msg.req.sdiag_protocol = IPPROTO_TCP;
    /* Бітова маска: запитуємо лише стан LISTEN */
    msg.req.idiag_states = (1 << TCP_LISTEN);
    /* Запитуємо розширену інформацію про пам'ять та параметри TCP */
    msg.req.idiag_ext = (1 << (INET_DIAG_INFO - 1));

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    return sendto(nl_fd, &msg, sizeof(msg), 0, (struct sockaddr *)&sa, sizeof(sa));
}
