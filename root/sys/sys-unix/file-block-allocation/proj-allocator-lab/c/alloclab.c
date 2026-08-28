/* alloclab.c — чотири способи записати той самий обсяг і карта, що з них вийшла.
   cc -O2 -Wall -o alloclab alloclab.c                                          */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/fiemap.h>
#include <linux/fs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

#define BATCH 512                       /* екстентів за один ioctl */
#define BLKSZ 4096ULL

struct plan {                           /* що саме різнить досліди */
    const char *name;
    size_t chunk;                       /* розмір однієї порції запису   */
    int    sync_each;                   /* fsync після кожної порції     */
    int    prealloc;                    /* сказати розмір наперед        */
    int    writers;                     /* скільки процесів пишуть разом */
};

static const struct plan PLANS[] = {
    { "4k-fsync",    4096,     1, 0, 1 },
    { "stream",      1u << 20, 0, 0, 1 },
    { "duet",        4096,     1, 0, 2 },
    { "duet-falloc", 4096,     1, 1, 2 },
};

struct map { unsigned long long extents, longest, meta; };

static int write_one(const char *path, const struct plan *pl, unsigned long long bytes)
{
    char *buf = malloc(pl->chunk);
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);

    if (fd < 0 || !buf) { perror(path); return -1; }
    memset(buf, 'x', pl->chunk);

    if (pl->prealloc && fallocate(fd, 0, 0, (off_t)bytes) < 0) {
        perror("fallocate");            /* EOPNOTSUPP тут теж поразка досліду */
        return -1;
    }
    for (unsigned long long off = 0; off < bytes; ) {
        size_t want = pl->chunk, done = 0;
        if (off + want > bytes) want = (size_t)(bytes - off);
        while (done < want) {
            ssize_t n = write(fd, buf + done, want - done);
            if (n < 0) { if (errno == EINTR) continue; perror("write"); return -1; }
            done += (size_t)n;
        }
        off += want;
        if (pl->sync_each && fsync(fd) < 0) { perror("fsync"); return -1; }
    }
    if (fsync(fd) < 0) { perror("fsync"); return -1; }
    free(buf);
    return close(fd);
}

static int map_file(const char *path, unsigned long long bytes, struct map *out)
{
    union {                             /* union, а не char[]: потрібне вирівнювання */
        struct fiemap fm;
        char raw[sizeof(struct fiemap) + BATCH * sizeof(struct fiemap_extent)];
    } q;
    unsigned long long next = 0;
    struct stat st;
    int fd, last = 0;

    memset(out, 0, sizeof(*out));
    if ((fd = open(path, O_RDONLY)) < 0) { perror(path); return -1; }

    while (!last) {
        memset(&q, 0, sizeof(q));
        q.fm.fm_start        = next;
        q.fm.fm_length       = FIEMAP_MAX_OFFSET;
        q.fm.fm_flags        = FIEMAP_FLAG_SYNC;   /* інакше побачимо намір */
        q.fm.fm_extent_count = BATCH;
        if (ioctl(fd, FS_IOC_FIEMAP, &q) < 0) { perror("FIEMAP"); close(fd); return -1; }
        if (q.fm.fm_mapped_extents == 0) break;

        for (unsigned i = 0; i < q.fm.fm_mapped_extents; i++) {
            struct fiemap_extent *e = &q.fm.fm_extents[i];
            out->extents++;
            if (e->fe_length > out->longest) out->longest = e->fe_length;
            next = e->fe_logical + e->fe_length;
            if (e->fe_flags & FIEMAP_EXTENT_LAST) last = 1;
        }
    }
    /* Дерево екстентів теж займає блоки, і ext4 враховує їх у st_blocks:
       усе, що обліковано понад округлені до блока дані, — це карта.      */
    if (fstat(fd, &st) == 0) {
        unsigned long long data = (bytes + BLKSZ - 1) / BLKSZ * BLKSZ;
        unsigned long long held = (unsigned long long)st.st_blocks * 512;
        out->meta = held > data ? held - data : 0;
    }
    close(fd);
    return 0;
}

int main(int argc, char **argv)
{
    unsigned long long bytes = 32ULL << 20;
    const char *dir = argc > 1 ? argv[1] : ".";
    char path[512];

    if (argc > 2) bytes = strtoull(argv[2], NULL, 10) << 20;
    printf("%-14s %10s %12s %10s\n", "strategy", "extents", "longest KiB", "map B");

    for (unsigned s = 0; s < sizeof PLANS / sizeof PLANS[0]; s++) {
        const struct plan *pl = &PLANS[s];
        pid_t kids[4];
        struct map m;

        for (int w = 0; w < pl->writers; w++) {
            snprintf(path, sizeof path, "%s/%s-%d.dat", dir, pl->name, w);
            if ((kids[w] = fork()) == 0)
                _exit(write_one(path, pl, bytes) == 0 ? 0 : 1);
        }
        for (int w = 0; w < pl->writers; w++) {
            int status;
            waitpid(kids[w], &status, 0);
            if (!WIFEXITED(status) || WEXITSTATUS(status)) {
                fprintf(stderr, "письменник упав на досліді %s\n", pl->name);
                return 1;
            }
        }
        snprintf(path, sizeof path, "%s/%s-0.dat", dir, pl->name);
        if (map_file(path, bytes, &m) < 0) return 1;
        printf("%-14s %10llu %12llu %10llu\n",
               pl->name, m.extents, m.longest >> 10, m.meta);
    }
    return 0;
}
