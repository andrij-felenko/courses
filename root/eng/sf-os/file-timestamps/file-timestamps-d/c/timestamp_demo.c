/* timestamp_demo.c — Читання через statx та модифікація через utimensat на C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <errno.h>

int inspect_and_touch(const char *filepath) {
    struct statx stx;
    memset(&stx, 0, sizeof(stx));

    /* Опитуємо метадані без розіменування посилань */
    if (statx(AT_FDCWD, filepath, AT_SYMLINK_NOFOLLOW, STATX_BASIC_STATS | STATX_BTIME, &stx) != 0) {
        perror("Помилка statx");
        return -1;
    }

    printf("Файл: %s\n", filepath);
    printf("  atime: %lld.%09u с\n", (long long)stx.stx_atime.tv_sec, stx.stx_atime.tv_nsec);
    printf("  mtime: %lld.%09u с\n", (long long)stx.stx_mtime.tv_sec, stx.stx_mtime.tv_nsec);
    printf("  ctime: %lld.%09u с\n", (long long)stx.stx_ctime.tv_sec, stx.stx_ctime.tv_nsec);

    if (stx.stx_mask & STATX_BTIME) {
        printf("  btime: %lld.%09u с (час народження підтримується)\n",
               (long long)stx.stx_btime.tv_sec, stx.stx_btime.tv_nsec);
    } else {
        printf("  btime: [не підтримується цією файловою системою]\n");
    }

    /* Оновлюємо лише mtime, atime залишаємо незмінним */
    struct timespec new_times[2];
    new_times[0].tv_sec = 0;
    new_times[0].tv_nsec = UTIME_OMIT; /* atime: без змін */
    new_times[1].tv_sec = 0;
    new_times[1].tv_nsec = UTIME_NOW;  /* mtime: поточний час ядра */

    if (utimensat(AT_FDCWD, filepath, new_times, 0) != 0) {
        perror("Помилка utimensat");
        return -1;
    }

    printf("Час mtime успішно оновлено.\n");
    return 0;
}
