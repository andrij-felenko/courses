/* Повертає дескриптор, який треба тримати відкритим до самої смерті:
   саме він і є заявою «примірник працює».
   Помилка EWOULDBLOCK означає «вже працює», решта — справжні збої.  */
static int claim_single_instance(const char *path)
{
    int fd, n, saved;
    char line[32];

    fd = open(path, O_RDWR | O_CREAT, 0644);   /* без O_CLOEXEC — див. нижче */
    if (fd < 0) return -1;

    if (flock(fd, LOCK_EX | LOCK_NB) != 0) {
        saved = errno;
        close(fd);
        errno = saved;
        return -1;
    }

    /* Номер процесу пишемо ПІСЛЯ взяття замка й винятково для людини:
       правду про зайнятість каже замок, а не вміст файлу.            */
    if (ftruncate(fd, 0) != 0) goto fail;
    n = snprintf(line, sizeof line, "%ld\n", (long) getpid());
    if (write_all(fd, line, (size_t) n) != 0) goto fail;

    return fd;
fail:
    saved = errno;
    close(fd);
    errno = saved;
    return -1;
}
