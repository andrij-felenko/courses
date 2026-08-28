/* 1. Сокет народжується неблокуючим — жодного fcntl. */
int fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
if (fd == -1)
    return -1;

/* 2. Запуск з'єднання. Успіх — це 0 АБО EINPROGRESS. */
if (connect(fd, (struct sockaddr *)&addr, sizeof addr) == -1 && errno != EINPROGRESS) {
    close(fd);
    return -1;
}

/* 3. ...після події готовности — перевірка відкладеної помилки (див. вище). */

/* 4. Читання: вибирати, доки не скаже EAGAIN. */
for (;;) {
    char    buf[16384];
    ssize_t n = recv(fd, buf, sizeof buf, 0);

    if (n > 0) {
        consume(buf, (size_t)n);
        continue;                          /* може бути ще — питаємо знову */
    }
    if (n == 0) {
        peer_closed(fd);                   /* упорядковане закриття */
        break;
    }
    if (errno == EINTR)
        continue;                          /* сигнал — просто повторити */
    if (errno == EAGAIN || errno == EWOULDBLOCK)
        break;                             /* усе вибрано — назад у цикл подій */

    fail(fd, errno);                       /* оце вже справжня помилка */
    break;
}
