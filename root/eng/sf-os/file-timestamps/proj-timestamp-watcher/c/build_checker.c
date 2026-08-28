/* build_checker.c — Аналізатор залежностей на базі statx та utimensat */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>
#include <errno.h>

typedef struct {
    long long sec;
    unsigned int nsec;
    bool has_btime;
    long long btime_sec;
    unsigned int btime_nsec;
} FileMeta;

static int fetch_file_meta(const char *path, FileMeta *meta) {
    struct statx stx;
    memset(&stx, 0, sizeof(stx));

    if (statx(AT_FDCWD, path, AT_SYMLINK_NOFOLLOW, STATX_MTIME | STATX_BTIME, &stx) != 0) {
        return -1;
    }

    meta->sec = (long long)stx.stx_mtime.tv_sec;
    meta->nsec = stx.stx_mtime.tv_nsec;

    if (stx.stx_mask & STATX_BTIME) {
        meta->has_btime = true;
        meta->btime_sec = (long long)stx.stx_btime.tv_sec;
        meta->btime_nsec = stx.stx_btime.tv_nsec;
    } else {
        meta->has_btime = false;
    }

    return 0;
}

static int compare_timestamps(const FileMeta *a, const FileMeta *b) {
    if (a->sec != b->sec) {
        return (a->sec > b->sec) ? 1 : -1;
    }
    if (a->nsec != b->nsec) {
        return (a->nsec > b->nsec) ? 1 : -1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <source_file> <target_file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *src_path = argv[1];
    const char *tgt_path = argv[2];

    FileMeta src_meta, tgt_meta;

    if (fetch_file_meta(src_path, &src_meta) != 0) {
        fprintf(stderr, "Помилка читання джерела %s: %s\n", src_path, strerror(errno));
        return EXIT_FAILURE;
    }

    bool target_exists = (fetch_file_meta(tgt_path, &tgt_meta) == 0);

    printf("=== Аналіз часових позначок збірки ===\n");
    printf("Джерело: %s -> mtime = %lld.%09u с\n", src_path, src_meta.sec, src_meta.nsec);

    if (!target_exists) {
        printf("Ціль:    %s [відсутня, потрібна початкова збірка]\n", tgt_path);
    } else {
        printf("Ціль:    %s -> mtime = %lld.%09u с\n", tgt_path, tgt_meta.sec, tgt_meta.nsec);
    }

    bool need_rebuild = false;

    if (!target_exists) {
        need_rebuild = true;
    } else {
        int cmp = compare_timestamps(&src_meta, &tgt_meta);
        if (cmp > 0) {
            printf("Статус:  Ціль застаріла (джерело новіше за артефакт).\n");
            need_rebuild = true;
        } else if (cmp == 0) {
            printf("УВАГА:   Позначки збігаються з точністю до наносекунд!\n");
            if (src_meta.nsec == 0 && tgt_meta.nsec == 0) {
                printf("ПОПЕРЕДЖЕННЯ: Файлова система має лише 1-секундну точність!\n");
            }
            need_rebuild = false;
        } else {
            printf("Статус:  Ціль актуальна (перезбірка не потрібна).\n");
            need_rebuild = false;
        }
    }

    if (need_rebuild) {
        printf("\nВиконується збірка артефакту...\n");
        int fd = open(tgt_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (fd < 0) {
            fprintf(stderr, "Не вдалося створити ціль: %s\n", strerror(errno));
            return EXIT_FAILURE;
        }
        dprintf(fd, "Compiled artifact at %ld\n", time(NULL));
        close(fd);

        /* Фіксуємо новий час через utimensat */
        struct timespec ts[2];
        ts[0].tv_sec = 0;
        ts[0].tv_nsec = UTIME_OMIT; /* atime не чіпаємо */
        ts[1].tv_sec = 0;
        ts[1].tv_nsec = UTIME_NOW;  /* mtime = поточний час */

        if (utimensat(AT_FDCWD, tgt_path, ts, 0) != 0) {
            fprintf(stderr, "Помилка оновлення позначки: %s\n", strerror(errno));
            return EXIT_FAILURE;
        }
        printf("Збірку завершено успішно. Часову позначку оновлено.\n");
    }

    return EXIT_SUCCESS;
}
