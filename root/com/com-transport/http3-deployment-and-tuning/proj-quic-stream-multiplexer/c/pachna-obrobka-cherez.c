struct mmsghdr msgs[64];
struct iovec iovecs[64];
uint8_t buffers[64][2000];

for (int i = 0; i < 64; i++) {
    iovecs[i].iov_base = buffers[i];
    iovecs[i].iov_len = sizeof(buffers[i]);
    msgs[i].msg_hdr.msg_iov = &iovecs[i];
    msgs[i].msg_hdr.msg_iovlen = 1;
}

int retval = recvmmsg(sockfd, msgs, 64, MSG_DONTWAIT, NULL);
