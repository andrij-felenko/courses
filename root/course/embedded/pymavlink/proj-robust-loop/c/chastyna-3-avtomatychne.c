#define RECONNECT_MIN_S 0.5     // перша пауза між спробами
#define RECONNECT_MAX_S 5.0     // стеля паузи (backoff далі не росте)

// open_serial(), wait_readable(), sleep_s() — дрібні помічники, зібрані у складеному лістингу нижче.

// Одна спроба підключитись і дочекатися апарата.
// Повертає fd живої лінії або -1. НІКОЛИ не блокує назавжди.
static int link_connect(const char *dev, LinkState *st) {
    int fd = open_serial(dev, BAUD);
    if (fd < 0) { perror("[CONN] open"); return -1; }

    // чекаємо перший heartbeat З ТАЙМАУТОМ — без нього зависли б навіки на мертвій лінії
    double deadline = now_monotonic() + RECONNECT_MAX_S;
    for (;;) {
        double left = deadline - now_monotonic();
        if (left <= 0.0) { close(fd); return -1; }   // не дочекались — закрити fd (проти витоку)
        if (wait_readable(fd, left) <= 0) continue;  // poll: даних нема — чекаємо до дедлайну

        uint8_t buf[512];
        ssize_t n = read(fd, buf, sizeof buf);
        if (n <= 0) {
            if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) continue;
            close(fd); return -1;
        }
        for (ssize_t i = 0; i < n; i++) {
            mavlink_message_t msg;
            mavlink_status_t status;
            if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &msg, &status)
                && msg.msgid == MAVLINK_MSG_ID_HEARTBEAT) {
                st->target_system = msg.sysid;
                st->target_component = msg.compid;
                st->last_heartbeat = now_monotonic();   // ← лінія ДОВЕДЕНО жива: стамкуємо час
                printf("[CONN] апарат на лінії: sys %d, comp %d\n",
                       msg.sysid, msg.compid);
                return fd;
            }
        }
    }
}

// Закрити стару лінію (проти витоку) і піднімати нову з backoff.
static int link_reconnect(const char *dev, int old_fd, LinkState *st) {
    if (old_fd >= 0) close(old_fd);   // ПЕРШ НІЖ відкрити нову — закрити стару!

    double delay = RECONNECT_MIN_S;
    for (;;) {
        int fd = link_connect(dev, st);
        if (fd >= 0) return fd;
        printf("[CONN] не вдалось; повтор через %.1f с\n", delay);
        sleep_s(delay);                              // єдиний свідомий sleep — коли лінії НЕМАЄ
        delay = delay * 2 > RECONNECT_MAX_S           // backoff: пауза росте до стелі
                    ? RECONNECT_MAX_S : delay * 2;
    }
}
