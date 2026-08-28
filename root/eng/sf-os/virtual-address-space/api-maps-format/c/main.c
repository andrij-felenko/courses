#define _GNU_SOURCE
#include <fcntl.h>
#include <linux/fs.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "вжиток: %s <pid> <адреса-16>\n", argv[0]);
        return 2;
    }

    char path[64];
    snprintf(path, sizeof path, "/proc/%s/maps", argv[1]);

    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        perror(path);
        return 1;
    }

    char name[256] = "";
    struct procmap_query q;

    memset(&q, 0, sizeof q);          /* обнулити ОБОВ'ЯЗКОВО: структура росте */
    q.size          = sizeof q;       /* за цим числом ядро добирає набір полів */
    q.query_addr    = strtoull(argv[2], NULL, 16);
    q.query_flags   = PROCMAP_QUERY_COVERING_OR_NEXT_VMA;
    q.vma_name_addr = (uint64_t)(uintptr_t)name;
    q.vma_name_size = sizeof name;

    if (ioctl(fd, PROCMAP_QUERY, &q) < 0) {
        perror("PROCMAP_QUERY");      /* ENOENT — жодної ділянки за цією адресою */
        close(fd);
        return 1;
    }

    printf("%llx-%llx %c%c%c%c зсув %llx  %x:%x  inode %llu  %s\n",
           (unsigned long long)q.vma_start,
           (unsigned long long)q.vma_end,
           q.vma_flags & PROCMAP_QUERY_VMA_READABLE   ? 'r' : '-',
           q.vma_flags & PROCMAP_QUERY_VMA_WRITABLE   ? 'w' : '-',
           q.vma_flags & PROCMAP_QUERY_VMA_EXECUTABLE ? 'x' : '-',
           q.vma_flags & PROCMAP_QUERY_VMA_SHARED     ? 's' : 'p',
           (unsigned long long)q.vma_offset,
           q.dev_major, q.dev_minor,
           (unsigned long long)q.inode,
           q.vma_name_size ? name : "");   /* нуль на виході = імені немає */

    close(fd);
    return 0;
}
