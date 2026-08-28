int epoll_wait(int epfd, struct epoll_event *events,
               int maxevents, int timeout);

int epoll_pwait(int epfd, struct epoll_event *events,
                int maxevents, int timeout,
                const sigset_t *sigmask);                    /* 2.6.19 */

int epoll_pwait2(int epfd, struct epoll_event *events,
                 int maxevents, const struct timespec *timeout,
                 const sigset_t *sigmask);                   /* 5.11 */
