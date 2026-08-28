#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/udp.h>
#include <arpa/inet.h>

ssize_t send_udp_gso_c(int sockfd, const struct sockaddr_in *dst_addr,
                       const void *data, size_t data_len, uint16_t segment_size) {
    struct iovec iov;
    iov.iov_base = (void *)data;
    iov.iov_len = data_len;

    char cbuf[CMSG_SPACE(sizeof(uint16_t))];
    memset(cbuf, 0, sizeof(cbuf));

    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_name = (void *)dst_addr;
    msg.msg_namelen = sizeof(*dst_addr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cbuf;
    msg.msg_controllen = sizeof(cbuf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_UDP;
    cmsg->cmsg_type = UDP_SEGMENT;
    cmsg->cmsg_len = CMSG_LEN(sizeof(uint16_t));
    
    uint16_t *val_ptr = (uint16_t *)CMSG_DATA(cmsg);
    *val_ptr = segment_size;

    return sendmsg(sockfd, &msg, 0);
}
