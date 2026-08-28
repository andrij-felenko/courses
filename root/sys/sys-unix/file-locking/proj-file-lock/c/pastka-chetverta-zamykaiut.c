/* Замок узято на об'єкті, а перевіряємо ми ім'я — тому звіряти
   треба після взяття, а не до нього.                                */
static int lock_by_path(const char *path)
{
    struct stat by_fd, by_name;
    int attempt, fd, saved;

    for (attempt = 0; attempt < 8; attempt++) {
        fd = open(path, O_RDWR | O_CREAT | O_CLOEXEC, 0644);
        if (fd < 0) return -1;

        if (flock(fd, LOCK_EX) != 0) goto give_up;
        if (fstat(fd, &by_fd) != 0)  goto give_up;

        if (stat(path, &by_name) == 0
            && by_name.st_dev == by_fd.st_dev
            && by_name.st_ino == by_fd.st_ino)
            return fd;                 /* ім'я веде сюди — замок справжній */

        close(fd);                     /* нас замкнули на викинутому файлі */
    }
    errno = ESTALE;
    return -1;

give_up:
    saved = errno;
    close(fd);
    errno = saved;
    return -1;
}
