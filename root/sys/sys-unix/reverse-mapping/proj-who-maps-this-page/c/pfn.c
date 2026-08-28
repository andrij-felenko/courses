/* pfn.c — у який фізичний кадр дивиться ця віртуальна адреса.
 *   cc -O2 -Wall -o pfn pfn.c
 *   sudo ./pfn 1234 0x7f2a4c014000
 */
#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <fcntl.h>
#include <unistd.h>

static uint64_t read_u64(const char *path, off_t off)
{
    uint64_t v = 0;
    int fd = open(path, O_RDONLY);
    if (fd < 0) { perror(path); exit(1); }
    if (pread(fd, &v, 8, off) != 8) { perror("pread"); exit(1); }
    close(fd);
    return v;
}

int main(int argc, char **argv)
{
    if (argc != 3) { fprintf(stderr, "вжиток: %s <pid> <адреса>\n", argv[0]); return 2; }

    char path[64];
    uint64_t va = strtoull(argv[2], NULL, 0);
    snprintf(path, sizeof path, "/proc/%s/pagemap", argv[1]);

    uint64_t e = read_u64(path, (off_t)(va / 4096 * 8));
    if (!(e & (1ULL << 63))) { puts("кадру немає: сторінка не в пам'яті"); return 1; }

    uint64_t pfn = e & ((1ULL << 55) - 1);
    if (!pfn) { puts("кадр 0 — найпевніше бракує CAP_SYS_ADMIN"); return 1; }

    printf("кадр %#" PRIx64 ", відображень %" PRIu64 "\n",
           pfn, read_u64("/proc/kpagecount", (off_t)(pfn * 8)));
    return 0;
}
