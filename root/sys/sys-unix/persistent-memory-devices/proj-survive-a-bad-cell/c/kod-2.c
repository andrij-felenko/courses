/* Вирізати дірку й перезаписати. Обидва рухи йдуть ЧЕРЕЗ ДРАЙВЕР — і лише
   тому носій дізнається, що ділянку час прибрати зі списку. */
static int repair(int fd, off_t off, size_t len)
{
    void *zeros;
    int rc;

    if (fallocate(fd, FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE,
                  off, (off_t)len) < 0)
        return -1;

    zeros = calloc(1, len);
    if (!zeros) return -1;

    /* Виділяючи блоки під цей запис, файлова система зануляє їх через
       драйвер, а драйвер, побачивши в діапазоні биту ділянку, замовляє
       прошивці планки очищення й викидає ділянку зі списку. */
    rc = (pwrite(fd, zeros, len, off) == (ssize_t)len) ? 0 : -1;
    free(zeros);
    return rc ? rc : fsync(fd);
}
