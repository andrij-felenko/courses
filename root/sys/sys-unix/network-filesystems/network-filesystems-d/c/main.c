int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
if (fd < 0) return -1;

if (write(fd, buf, len) != (ssize_t)len) {   /* тут помилки може ще не бути */
    close(fd);
    return -1;
}
if (fsync(fd) < 0) {         /* просимо сервер закріпити дані НА НОСІЇ */
    close(fd);
    return -1;
}
if (close(fd) < 0)           /* і лише тут дізнаємося решту правди */
    return -1;

return 0;
