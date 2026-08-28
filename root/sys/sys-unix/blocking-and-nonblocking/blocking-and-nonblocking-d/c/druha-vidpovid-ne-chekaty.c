ssize_t n = read(fd, buf, sizeof buf);
if (n > 0) {
    consume(buf, n);                 /* прийшли дані   */
} else if (n == 0) {
    peer_closed(fd);                 /* інший бік закрив з'єднання */
} else if (errno == EAGAIN || errno == EWOULDBLOCK) {
    /* даних немає — це нормальний хід подій, не збій */
} else if (errno == EINTR) {
    /* виклик перервано сигналом — повторити */
} else {
    fail(fd, errno);                 /* оце вже справжня помилка */
}
