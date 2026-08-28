int             fd;                       /* що передаємо */
char            byte = 'x';
struct iovec    iov  = { .iov_base = &byte, .iov_len = 1 };
union {                                   /* union дає буферу правильне вирівнювання */
    char           buf[CMSG_SPACE(sizeof(int))];
    struct cmsghdr align;
} u = { 0 };
struct msghdr   msg  = { 0 };

msg.msg_iov        = &iov;
msg.msg_iovlen     = 1;
msg.msg_control    = u.buf;
msg.msg_controllen = sizeof u.buf;        /* поки що — щоб CMSG_FIRSTHDR побачив місце */

struct cmsghdr *c = CMSG_FIRSTHDR(&msg);
c->cmsg_level = SOL_SOCKET;
c->cmsg_type  = SCM_RIGHTS;
c->cmsg_len   = CMSG_LEN(sizeof(int));
memcpy(CMSG_DATA(c), &fd, sizeof(int));
msg.msg_controllen = c->cmsg_len;         /* ← тепер сума заповненого, не розмір буфера */

if (sendmsg(sock, &msg, 0) < 0)
    perror("sendmsg");
