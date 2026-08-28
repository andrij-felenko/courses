#include <stdint.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

/* Скільки призначень справді збіглося й дістало спільні блоки; -1 — помилка. */
int dedupe_range(int src_fd, uint64_t off, uint64_t len,
                 const int *dst_fd, const uint64_t *dst_off, unsigned n)
{
    size_t sz = sizeof(struct file_dedupe_range)
              + (size_t)n * sizeof(struct file_dedupe_range_info);

    /* calloc, а не malloc: усі reserved мусять бути нулями. */
    struct file_dedupe_range *arg = calloc(1, sz);
    if (!arg)
        return -1;

    arg->src_offset = off;
    arg->src_length = len;
    arg->dest_count = n;
    for (unsigned i = 0; i < n; i++) {
        arg->info[i].dest_fd = dst_fd[i];
        arg->info[i].dest_offset = dst_off[i];
    }

    int same = -1;
    if (ioctl(src_fd, FIDEDUPERANGE, arg) == 0) {
        same = 0;
        for (unsigned i = 0; i < n; i++)
            if (arg->info[i].status == FILE_DEDUPE_RANGE_SAME
                && arg->info[i].bytes_deduped > 0)
                same++;
    }
    free(arg);
    return same;
}
