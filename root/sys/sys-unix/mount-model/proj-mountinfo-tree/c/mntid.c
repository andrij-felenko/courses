/* cc -O2 -o mntid mntid.c ; потрібне ядро 5.8+ */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>

int main(int argc, char **argv) {
    struct statx sx;
    if (argc < 2) { fputs("вжиток: mntid <шлях>\n", stderr); return 2; }
    if (statx(AT_FDCWD, argv[1], 0, STATX_MNT_ID, &sx) < 0) { perror("statx"); return 1; }
    if (!(sx.stx_mask & STATX_MNT_ID)) { fputs("ядро не віддало mnt_id\n", stderr); return 1; }
    printf("%s -> монтування %llu\n", argv[1], (unsigned long long)sx.stx_mnt_id);
    return 0;
}
