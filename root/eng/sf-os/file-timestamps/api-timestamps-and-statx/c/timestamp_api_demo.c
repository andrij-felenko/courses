/* timestamp_api_demo.c — Робота з statx та utimensat на мові C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>
#include <errno.h>

int print_file_timestamps(const char *filepath) {
    struct statx stx;
    memset(&stx, 0, sizeof(stx));

    /* Запитуємо всі доступні метадані без автоматичного монтування */
    if (statx(AT_FDCWD, filepath, AT_SYMLINK_NOFOLLOW | AT_NO_AUTOMOUNT,
              STATX_BASIC_STATS | STATX_BTIME, &stx) != 0) {
        fprintf(stderr, "Помилка statx для %s: %s\n", filepath, strerror(errno));
        return -1;
    }

    printf("Звіт часових позначок для файлу: %s\n", filepath);
    printf("  atime (доступ):     %lld.%09u с\n",
           (long long)stx.stx_atime.tv_sec, stx.stx_atime.tv_nsec);
    printf("  mtime (вміст):      %lld.%09u с\n",
           (long long)stx.stx_mtime.tv_sec, stx.stx_mtime.tv_nsec);
    printf("  ctime (метадані):   %lld.%09u с\n",
           (long long)stx.stx_ctime.tv_sec, stx.stx_ctime.tv_nsec);

    if (stx.stx_mask & STATX_BTIME) {
        printf("  btime (створення):  %lld.%09u с [підтримується ФС]\n",
               (long long)stx.stx_btime.tv_sec, stx.stx_btime.tv_nsec);
    } else {
        printf("  btime (створення):  [не підтримується драйвером ФС]\n");
    }

    return 0;
}

int touch_modification_only(const char *filepath) {
    struct timespec ts[2];

    /* times[0] = atime: не чіпати */
    ts[0].tv_sec = 0;
    ts[0].tv_nsec = UTIME_OMIT;

    /* times[1] = mtime: встановити точний поточний системний час */
    ts[1].tv_sec = 0;
    ts[1].tv_nsec = UTIME_NOW;

    if (utimensat(AT_FDCWD, filepath, ts, 0) != 0) {
        fprintf(stderr, "Помилка utimensat для %s: %s\n", filepath, strerror(errno));
        return -1;
    }

    printf("Позначку mtime для %s успішно оновлено (atime не змінювався).\n", filepath);
    return 0;
}
