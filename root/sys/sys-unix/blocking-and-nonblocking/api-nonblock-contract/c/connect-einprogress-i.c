int rc = connect(fd, (struct sockaddr *)&addr, sizeof addr);
if (rc == 0) {
    connected(fd);                       /* устигло за один виклик */
} else if (errno != EINPROGRESS) {
    fail(fd, errno);                     /* миттєва відмова */
} else {
    /* чекаємо EPOLLOUT; на невдачі ядро додасть EPOLLERR */
    struct epoll_event ev = { .events = EPOLLOUT, .data.fd = fd };
    epoll_ctl(ep, EPOLL_CTL_ADD, fd, &ev);
}

/* ...коли epoll_wait віддав подію на цьому fd: */
int       err = 0;
socklen_t len = sizeof err;
if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &err, &len) == -1)
    err = errno;                         /* про запас: є системи, де відкладену
                                            помилку віддають саме так */
if (err == 0)
    connected(fd);
else
    fail(fd, err);                       /* ECONNREFUSED, ETIMEDOUT, EHOSTUNREACH… */
