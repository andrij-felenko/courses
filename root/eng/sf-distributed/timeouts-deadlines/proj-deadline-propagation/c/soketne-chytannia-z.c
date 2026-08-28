/* Читання рівно n байтів із сокета з жорстким дотриманням дедлайну */
int read_exact_with_deadline(int sock_fd, void *buf, size_t count, const deadline_context_t *ctx) {
    uint8_t *ptr = (uint8_t *)buf;
    size_t bytes_left = count;

    while (bytes_left > 0) {
        int64_t remain_ms = context_remaining_ms(ctx);
        if (remain_ms <= 0) {
            errno = ETIMEDOUT;
            return -1; /* Дедлайн сплив під час читання */
        }

        struct pollfd pfd;
        pfd.fd = sock_fd;
        pfd.events = POLLIN;
        pfd.revents = 0;

        int ret = poll(&pfd, 1, (int)remain_ms);
        if (ret < 0) {
            if (errno == EINTR) {
                continue; /* Переривання сигналом — перевіряємо час і повторюємо */
            }
            return -1;    /* Системна помилка */
        }
        if (ret == 0) {
            errno = ETIMEDOUT;
            return -1;    /* Таймаут poll */
        }

        if (pfd.revents & (POLLERR | POLLHUP | POLLNVAL)) {
            errno = ECONNRESET;
            return -1;
        }

        if (pfd.revents & POLLIN) {
            ssize_t n = recv(sock_fd, ptr, bytes_left, MSG_DONTWAIT);
            if (n < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) {
                    continue;
                }
                return -1;
            }
            if (n == 0) {
                errno = ECONNABORTED; /* Передчасне закриття сокета іншим боком */
                return -1;
            }
            ptr += n;
            bytes_left -= n;
        }
    }
    return 0; /* Усі байти успішно зчитано в межах бюджету */
}
