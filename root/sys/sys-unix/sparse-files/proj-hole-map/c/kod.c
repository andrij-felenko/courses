enum { WALK_OK = 0, WALK_NO_MAP = 1, WALK_ERROR = -1 };

static int copy_by_map(int sfd, int dfd, off_t size, char *buf, size_t bufsz,
                       off_t *moved, long *islands)
{
    off_t pos = 0;
    while (pos < size) {
        off_t data = lseek(sfd, pos, SEEK_DATA);
        if (data < 0) {
            if (errno == ENXIO) break;          /* далі до кінця сама діра */
            if (errno == EINVAL || errno == EOPNOTSUPP)
                return WALK_NO_MAP;             /* цих питань тут не розуміють */
            return WALK_ERROR;
        }
        off_t end = lseek(sfd, data, SEEK_HOLE);
        if (end < 0) return WALK_ERROR;         /* не станеться: кінець файлу — теж діра */
        if (end > size) end = size;             /* файл міг вирости під нами */
        if (end <= data) break;                 /* карта не рухається — виходимо */

        (*islands)++;
        for (off_t off = data; off < end; ) {
            size_t want = bufsz;
            if ((off_t)want > end - off) want = (size_t)(end - off);
            ssize_t got = pread_full(sfd, buf, want, off);
            if (got < 0) return WALK_ERROR;
            if (got == 0) { end = off; break; } /* джерело вкоротили під нами */
            if (pwrite_full(dfd, buf, (size_t)got, off) < 0) return WALK_ERROR;
            *moved += got;
            off += got;
        }
        pos = end;
    }
    return WALK_OK;
}
