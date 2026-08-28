static int copy_scanning(int sfd, int dfd, off_t size, char *buf, size_t bufsz,
                         int punch, off_t *moved, off_t *skipped)
{
    for (off_t off = 0; off < size; ) {
        size_t want = bufsz;
        if ((off_t)want > size - off) want = (size_t)(size - off);
        ssize_t got = pread_full(sfd, buf, want, off);
        if (got < 0) return -1;
        if (got == 0) break;
        if (punch && all_zero(buf, (size_t)got)) {
            *skipped += got;                    /* нічого не пишемо — тут буде діра */
        } else {
            if (pwrite_full(dfd, buf, (size_t)got, off) < 0) return -1;
            *moved += got;
        }
        off += got;
    }
    return 0;
}
