struct msghdr msg = {0};
struct cmsghdr *cmsg;
char buf[CMSG_SPACE(sizeof(int))];
char payload = 'F';
struct iovec iov = { .iov_base = &payload, .iov_len = 1 };

/* хоча б один байт корисних даних: без нього дескриптор не передасться */
msg.msg_iov = &iov;
msg.msg_iovlen = 1;
msg.msg_control = buf;
msg.msg_controllen = sizeof(buf);

cmsg = CMSG_FIRSTHDR(&msg);
cmsg->cmsg_level = SOL_SOCKET;
cmsg->cmsg_type = SCM_RIGHTS;
cmsg->cmsg_len = CMSG_LEN(sizeof(int));

*((int *) CMSG_DATA(cmsg)) = dmabuf_fd;

sendmsg(socket_fd, &msg, 0);
