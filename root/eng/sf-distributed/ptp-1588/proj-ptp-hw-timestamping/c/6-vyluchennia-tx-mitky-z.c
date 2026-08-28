struct msghdr msg;
struct iovec iov;
char control[512];
uint8_t dummy_buf[256];

memset(&msg, 0, sizeof(msg));
iov.iov_base = dummy_buf;
iov.iov_len = sizeof(dummy_buf);
msg.msg_iov = &iov;
msg.msg_iovlen = 1;
msg.msg_control = control;
msg.msg_controllen = sizeof(control);

// Читання виключно з черги помилок
int res = recvmsg(sock_fd, &msg, MSG_ERRQUEUE);
if (res >= 0) {
    for (struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg); cmsg != NULL; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            struct timespec *ts = (struct timespec *)CMSG_DATA(cmsg);
            // ts[2] - апаратна мітка PHC (найточніша)
            printf("TX Hardware Timestamp (t1): %ld.%09ld s\n", ts[2].tv_sec, ts[2].tv_nsec);
        }
    }
}
