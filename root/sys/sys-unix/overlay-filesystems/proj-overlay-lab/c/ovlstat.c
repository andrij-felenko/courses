/* ovlstat.c — тотожність файлу: чия файлова система, який inode, скільки імен */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

static const char *kind(unsigned mode)
{
    switch (mode & S_IFMT) {
    case S_IFREG: return "файл";
    case S_IFDIR: return "каталог";
    case S_IFCHR: return "симв.пристрій";
    case S_IFBLK: return "блок.пристрій";
    case S_IFLNK: return "символьне посилання";
    default:      return "інше";
    }
}

int main(int argc, char **argv)
{
    for (int i = 1; i < argc; i++) {
        struct statx sx;

        if (statx(AT_FDCWD, argv[i],
                  AT_SYMLINK_NOFOLLOW | AT_STATX_SYNC_AS_STAT,
                  STATX_TYPE | STATX_MODE | STATX_NLINK |
                  STATX_INO | STATX_SIZE, &sx) < 0) {
            printf("%-22s — %s\n", argv[i], strerror(errno));
            continue;
        }

        printf("%-22s fs=%u:%-3u ino=%-9llu nlink=%-2u %s",
               argv[i], sx.stx_dev_major, sx.stx_dev_minor,
               (unsigned long long)sx.stx_ino, sx.stx_nlink,
               kind(sx.stx_mode));

        if (S_ISCHR(sx.stx_mode) || S_ISBLK(sx.stx_mode))
            printf(" %u/%u", sx.stx_rdev_major, sx.stx_rdev_minor);
        else if (S_ISREG(sx.stx_mode))
            printf(" %llu Б", (unsigned long long)sx.stx_size);

        printf("\n");
    }
    return 0;
}
