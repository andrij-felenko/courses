/* emfile.c — EMFILE, крутіння вхолосту й резервний дескриптор */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/epoll.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <netinet/in.h>

static int reserve;                        /* число, яке тримаємо про запас */

static void refuse_one(int srv)
{
    close(reserve);                        /* звільнили одне число */
    int c = accept(srv, NULL, NULL);       /* тепер є куди прийняти */
    if (c >= 0) {
        send(c, "503\n", 4, MSG_NOSIGNAL); /* чесна відмова замість мовчанки */
        close(c);
    }
    reserve = open("/dev/null", O_RDONLY); /* і знову беремо запас */
}

int main(void)
{
    struct sockaddr_in a = { .sin_family = AF_INET };
    socklen_t alen = sizeof a;
    struct rlimit rl;
    struct epoll_event ev = { .events = EPOLLIN };
    int srv, ep;

    getrlimit(RLIMIT_NOFILE, &rl);
    rl.rlim_cur = 64;                      /* штучна стеля замість справжньої */
    setrlimit(RLIMIT_NOFILE, &rl);

    srv = socket(AF_INET, SOCK_STREAM, 0);
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    bind(srv, (struct sockaddr *)&a, sizeof a);
    listen(srv, 128);
    getsockname(srv, (struct sockaddr *)&a, &alen);

    ep = epoll_create1(0);                 /* заводимо ДО вичерпання чисел */
    ev.data.fd = srv;
    epoll_ctl(ep, EPOLL_CTL_ADD, srv, &ev);
    reserve = open("/dev/null", O_RDONLY);

    for (int i = 0; i < 8; i++) {          /* клієнти стукають — ми не приймаємо */
        int c = socket(AF_INET, SOCK_STREAM, 0);
        connect(c, (struct sockaddr *)&a, sizeof a);
    }
    while (open("/dev/null", O_RDONLY) >= 0)
        ;                                  /* вигрібаємо решту вільних чисел */

    for (int spin = 1; spin <= 5; spin++) {
        epoll_wait(ep, &ev, 1, -1);        /* повертається МИТТЄВО */
        int c = accept(srv, NULL, NULL);
        printf("прохід %d: epoll — «готовий», accept — %s\n",
               spin, c < 0 ? strerror(errno) : "прийнято");
    }

    puts("--- вмикаємо резерв ---");
    int refused = 0;
    while (epoll_wait(ep, &ev, 1, 0) > 0) {
        refuse_one(srv);
        refused++;
    }
    printf("відмовлено %d з'єднанням; черга порожня, цикл засинає\n", refused);
    return 0;
}
