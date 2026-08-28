struct align { size_t mem, off; };

static struct align dio_align(int fd)
{
    struct align a = { 4096, 4096 };     /* безпечна стеля, якщо не відповіли */
    struct statx stx;

    if (statx(fd, "", AT_EMPTY_PATH, STATX_DIOALIGN, &stx) == 0
        && (stx.stx_mask & STATX_DIOALIGN) && stx.stx_dio_mem_align) {
        a.mem = stx.stx_dio_mem_align;
        a.off = stx.stx_dio_offset_align;
    }
    return a;
}
