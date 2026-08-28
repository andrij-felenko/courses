/* budget.c — скільки коштує одне з'єднання.  cc -O2 -o budget budget.c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define PAIRS 5000

/* рядок виду "Slab:   123456 kB" */
static long meminfo_kb(const char *key)
{
    char line[256]; long v = -1; size_t n = strlen(key);
    FILE *f = fopen("/proc/meminfo", "r");
    if (!f) return -1;
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, key, n)) { sscanf(line + n, " %ld", &v); break; }
    fclose(f);
    return v;
}

/* рядок виду "TCP: inuse 9 orphan 0 tw 2 alloc 24 mem 5" — mem у сторінках */
static long tcp_mem_pages(void)
{
    char line[256]; long v = -1;
    FILE *f = fopen("/proc/net/sockstat", "r");
    if (!f) return -1;
    while (fgets(line, sizeof line, f)) {
        if (strncmp(line, "TCP: ", 5)) continue;   /* не сплутати з TCPv6 */
        char *p = strstr(line, "mem ");
        if (p) sscanf(p + 4, "%ld", &v);
        break;
    }
    fclose(f);
    return v;
}

int main(void)
{
    struct sockaddr_in a = { .sin_family = AF_INET };
    socklen_t alen = sizeof a;
    struct rlimit rl;
    int srv, *fds;
    long slab0, mem0;

    getrlimit(RLIMIT_NOFILE, &rl);
    rl.rlim_cur = rl.rlim_max;             /* м'який ліміт піднімаємо самі */
    setrlimit(RLIMIT_NOFILE, &rl);

    srv = socket(AF_INET, SOCK_STREAM, 0);
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    a.sin_port = 0;                        /* вільний порт добере ядро */
    bind(srv, (struct sockaddr *)&a, sizeof a);
    listen(srv, 1024);
    getsockname(srv, (struct sockaddr *)&a, &alen);

    fds = malloc(sizeof(int) * PAIRS * 2);
    slab0 = meminfo_kb("Slab:");
    mem0  = tcp_mem_pages();

    for (int i = 0; i < PAIRS; i++) {
        int c = socket(AF_INET, SOCK_STREAM, 0);
        if (c < 0 || connect(c, (struct sockaddr *)&a, sizeof a) < 0) {
            perror("клієнт"); break;
        }
        int s = accept(srv, NULL, NULL);
        if (s < 0) { perror("accept"); break; }
        fds[2 * i] = c;
        fds[2 * i + 1] = s;

        if ((i + 1) % 1000 == 0) {
            long pages = tcp_mem_pages() - mem0;
            printf("%5d пар | Slab +%ld КіБ | черги %ld стор.\n",
                   i + 1, meminfo_kb("Slab:") - slab0, pages);
        }
    }

    char *buf = malloc(65536);
    memset(buf, 'x', 65536);
    for (int i = 0; i < PAIRS; i++)        /* наливаємо й НЕ читаємо */
        send(fds[2 * i], buf, 65536, MSG_DONTWAIT | MSG_NOSIGNAL);

    long pages = tcp_mem_pages() - mem0;
    printf("після наливання | Slab +%ld КіБ | черги %ld стор. (%ld МіБ)\n",
           meminfo_kb("Slab:") - slab0, pages, pages * 4 / 1024);
    return 0;
}
