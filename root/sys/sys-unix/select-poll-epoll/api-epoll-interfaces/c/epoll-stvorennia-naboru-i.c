#include <sys/epoll.h>

int epoll_create(int size);     /* size ігнорують з 2.6.8, але він мусить бути > 0 */
int epoll_create1(int flags);   /* 2.6.27; єдиний прапорець — EPOLL_CLOEXEC */

int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);

typedef union epoll_data {
    void    *ptr;
    int      fd;
    uint32_t u32;
    uint64_t u64;
} epoll_data_t;

struct epoll_event {
    uint32_t     events;   /* прапорці подій і режиму */
    epoll_data_t data;     /* вісім байтів, які ядро віддасть назад незміненими */
};
