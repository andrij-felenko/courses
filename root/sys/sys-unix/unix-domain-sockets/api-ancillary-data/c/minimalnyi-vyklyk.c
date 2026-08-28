char            byte;
struct iovec    iov = { .iov_base = &byte, .iov_len = 1 };
union {
    char           buf[CMSG_SPACE(8 * sizeof(int))];   /* максимум, який ми згодні взяти */
    struct cmsghdr align;
} u;
struct msghdr   msg = { 0 };

msg.msg_iov        = &iov;
msg.msg_iovlen     = 1;
msg.msg_control    = u.buf;
msg.msg_controllen = sizeof u.buf;

if (recvmsg(sock, &msg, MSG_CMSG_CLOEXEC) <= 0)
    return -1;

/* Спершу забираємо ВСЕ, що влізло, і лише потім дивимось на MSG_CTRUNC:
   ядро закрило само тільки той надлишок, який не вмістився, а те, що
   вмістилося, вже лежить у нашій таблиці й нікому, крім нас, не відоме. */
for (struct cmsghdr *c = CMSG_FIRSTHDR(&msg); c != NULL; c = CMSG_NXTHDR(&msg, c)) {
    if (c->cmsg_level != SOL_SOCKET || c->cmsg_type != SCM_RIGHTS)
        continue;
    int n = (c->cmsg_len - CMSG_LEN(0)) / sizeof(int);
    for (int i = 0; i < n; i++) {
        int got;
        memcpy(&got, CMSG_DATA(c) + i * sizeof(int), sizeof(int));
        /* … got належить нам, і закрити його теж нам */
    }
}
if (msg.msg_flags & MSG_CTRUNC)
    return -1;                            /* зібране вище закриваємо перед виходом */
