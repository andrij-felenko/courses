/* handleidx.c — покажчик файлів, ключем якого є рукоятка, а не ім'я.
 *   збирання: ./handleidx scan /srv/data index.txt
 *   звірка:   ./handleidx check index.txt
 * збірка:     cc -O2 -o handleidx handleidx.c
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <ftw.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>

static struct file_handle *fh;          /* один буфер на всю програму */
static FILE *idx;
static const char *uuid_of_mount(int id);

/* FNV-1a, 64 біти: дешева сума «чи змінився вміст», не криптографія. */
static unsigned long long content_sum(const char *path)
{
    unsigned long long h = 14695981039346656037ULL;
    unsigned char buf[1 << 16];
    ssize_t n;
    int fd = open(path, O_RDONLY);

    if (fd < 0)
        return 0;
    while ((n = read(fd, buf, sizeof buf)) > 0)
        for (ssize_t i = 0; i < n; i++)
            h = (h ^ buf[i]) * 1099511628211ULL;
    close(fd);
    return h;
}

static int visit(const char *path, const struct stat *st, int kind, struct FTW *w)
{
    int mount_id = -1;

    (void)w;
    if (kind != FTW_F || !S_ISREG(st->st_mode))
        return 0;

    /* handle_bytes виставляємо наново ПЕРЕД КОЖНИМ викликом: після вдалого
       виклику ядро лишає в ньому справжню довжину рукоятки (для ext4 — 8),
       і наступний файл на іншій ФС у цей огризок не влізе — прийде EOVERFLOW. */
    fh->handle_bytes = MAX_HANDLE_SZ;
    if (name_to_handle_at(AT_FDCWD, path, fh, &mount_id, 0) < 0) {
        if (errno != EOPNOTSUPP) {
            perror(path);
            return 0;
        }
        fh->handle_bytes = 0;       /* ФС кодувати не вміє — ключем лишиться шлях */
        fh->handle_type = -1;
        mount_id = -1;
    }

    fprintf(idx, "%s %d ", uuid_of_mount(mount_id), fh->handle_type);
    if (fh->handle_bytes)
        for (unsigned i = 0; i < fh->handle_bytes; i++)
            fprintf(idx, "%02x", fh->f_handle[i]);
    else
        fputc('-', idx);
    fprintf(idx, " %016llx %llu %zu %s\n", content_sum(path),
            (unsigned long long)st->st_size, strlen(path), path);
    return 0;
}

static int scan(const char *root, const char *out)
{
    if (!(idx = fopen(out, "w"))) {
        perror(out);
        return 1;
    }
    fputs("#handleidx 1\n"
          "#fields fs_uuid handle_type handle_hex fnv1a64 size path_len path\n", idx);
    if (nftw(root, visit, 32, FTW_PHYS) < 0) {
        perror(root);
        return 1;
    }
    return fclose(idx) != 0;
}
