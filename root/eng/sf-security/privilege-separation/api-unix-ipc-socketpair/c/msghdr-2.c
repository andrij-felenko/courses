int receive_fd(int socket) {
    struct msghdr msg = {0};
    char buf[1];
    struct iovec io = { .iov_base = buf, .iov_len = sizeof(buf) };

    union {
        char buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } cmsgu;

    msg.msg_iov = &io;
    msg.msg_iovlen = 1;
    msg.msg_control = cmsgu.buf;
    msg.msg_controllen = sizeof(cmsgu.buf);

    if (recvmsg(socket, &msg, 0) < 0) {
        return -1;
    }

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    if (cmsg && cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_RIGHTS) {
        int received_fd;
        memcpy(&received_fd, CMSG_DATA(cmsg), sizeof(int));
        return received_fd;
    }
    return -1;
}
