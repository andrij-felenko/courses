#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>

static void print_ts(const char *label, long long sec, unsigned nsec)
{
    char buf[64];
    time_t t = (time_t)sec;
    struct tm tm;
    localtime_r(&t, &tm);
    strftime(buf, sizeof buf, "%Y-%m-%d %H:%M:%S", &tm);
    printf("%-12s %s.%09u\n", label, buf, nsec);
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "вжиток: %s ШЛЯХ\n", argv[0]);
        return 2;
    }

    struct statx sx;
    unsigned mask = STATX_BASIC_STATS | STATX_BTIME | STATX_MNT_ID;

    if (statx(AT_FDCWD, argv[1], AT_SYMLINK_NOFOLLOW, mask, &sx) != 0) {
        if (errno != ENOSYS) {                 /* справжня помилка, не старе ядро */
            fprintf(stderr, "statx(%s): %s\n", argv[1], strerror(errno));
            return 1;
        }
        struct stat st;                        /* ядро до 4.11 — падаємо назад */
        if (fstatat(AT_FDCWD, argv[1], &st, AT_SYMLINK_NOFOLLOW) != 0) {
            fprintf(stderr, "fstatat(%s): %s\n", argv[1], strerror(errno));
            return 1;
        }
        printf("%-12s %u:%u\n", "пристрій", major(st.st_dev), minor(st.st_dev));
        printf("%-12s %llu\n", "inode", (unsigned long long)st.st_ino);
        printf("%-12s %llu\n", "імен", (unsigned long long)st.st_nlink);
        printf("%-12s %lld\n", "розмір", (long long)st.st_size);
        printf("%-12s %lld\n", "зайнято", (long long)st.st_blocks * 512);
        return 0;
    }

    /* stx_dev_* і stx_blksize маскою не покриті — вони є завжди */
    printf("%-12s %u:%u\n", "пристрій", sx.stx_dev_major, sx.stx_dev_minor);

    if (sx.stx_mask & STATX_INO)
        printf("%-12s %llu\n", "inode", (unsigned long long)sx.stx_ino);
    if (sx.stx_mask & STATX_NLINK)
        printf("%-12s %u\n", "імен", sx.stx_nlink);
    if (sx.stx_mask & STATX_TYPE)
        printf("%-12s %s\n", "тип",
               S_ISREG(sx.stx_mode) ? "звичайний файл" :
               S_ISDIR(sx.stx_mode) ? "каталог" :
               S_ISLNK(sx.stx_mode) ? "символьне посилання" : "інший");
    if (sx.stx_mask & STATX_MODE)
        printf("%-12s %04o\n", "права", sx.stx_mode & 07777);
    if (sx.stx_mask & STATX_SIZE)
        printf("%-12s %llu\n", "розмір", (unsigned long long)sx.stx_size);
    if (sx.stx_mask & STATX_BLOCKS)
        printf("%-12s %llu (%llu × 512)\n", "зайнято",
               (unsigned long long)sx.stx_blocks * 512,
               (unsigned long long)sx.stx_blocks);
    if (sx.stx_mask & STATX_MTIME)
        print_ts("змінено", sx.stx_mtime.tv_sec, sx.stx_mtime.tv_nsec);

    if (sx.stx_mask & STATX_BTIME)
        print_ts("створено", sx.stx_btime.tv_sec, sx.stx_btime.tv_nsec);
    else
        printf("%-12s ця файлова система часу створення не тримає\n", "створено");

    if (sx.stx_mask & STATX_MNT_ID)
        printf("%-12s %llu\n", "монтування", (unsigned long long)sx.stx_mnt_id);
    return 0;
}
