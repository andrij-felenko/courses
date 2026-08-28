#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/stat.h>
#include <errno.h>

#define BUF_SIZE (64 * 1024)

struct linux_dirent64 {
    unsigned long long d_ino;
    long long          d_off;
    unsigned short     d_reclen;
    unsigned char      d_type;
    char               d_name[];
};

typedef struct {
    unsigned long files_count;
    unsigned long dirs_count;
    unsigned long total_bytes;
} walk_stats_t;

static void process_directory_fd(int dir_fd, walk_stats_t *stats) {
    char *buf = malloc(BUF_SIZE);
    if (!buf) {
        perror("malloc");
        return;
    }

    while (1) {
        long nread = syscall(SYS_getdents64, dir_fd, buf, BUF_SIZE);
        if (nread == -1) {
            perror("getdents64");
            break;
        }
        if (nread == 0) {
            break; /* Кінця каталогу досягнуто */
        }

        for (long bpos = 0; bpos < nread; ) {
            struct linux_dirent64 *d = (struct linux_dirent64 *)(buf + bpos);
            unsigned char dtype = d->d_type;

            /* Ігноруємо спец-імена "." та ".." */
            if (strcmp(d->d_name, ".") == 0 || strcmp(d->d_name, "..") == 0) {
                bpos += d->d_reclen;
                continue;
            }

            /* Якщо тип невідомий файловій системі (DT_UNKNOWN), робимо fstatat */
            if (dtype == 0 /* DT_UNKNOWN */) {
                struct stat st;
                if (fstatat(dir_fd, d->d_name, &st, AT_SYMLINK_NOFOLLOW) == 0) {
                    if (S_ISDIR(st.st_mode)) dtype = 4; /* DT_DIR */
                    else if (S_ISREG(st.st_mode)) dtype = 8; /* DT_REG */
                }
            }

            if (dtype == 4 /* DT_DIR */) {
                stats->dirs_count++;
                /* O_NOFOLLOW: якщо запис устигли підмінити посиланням — ELOOP, а не перехід */
                int child_fd = openat(dir_fd, d->d_name, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
                if (child_fd != -1) {
                    process_directory_fd(child_fd, stats);
                    close(child_fd);
                }
            } else if (dtype == 8 /* DT_REG */) {
                stats->files_count++;
            }

            bpos += d->d_reclen;
        }
    }

    free(buf);
}

int main(int argc, char *argv[]) {
    const char *start_path = (argc > 1) ? argv[1] : ".";
    int root_fd = open(start_path, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (root_fd == -1) {
        fprintf(stderr, "Не вдалося відкрити каталог %s: %s\n", start_path, strerror(errno));
        return EXIT_FAILURE;
    }

    walk_stats_t stats = {0, 0, 0};
    process_directory_fd(root_fd, &stats);
    close(root_fd);

    printf("Знайдено каталогів: %lu, файлів: %lu\n", stats.dirs_count, stats.files_count);
    return EXIT_SUCCESS;
}
