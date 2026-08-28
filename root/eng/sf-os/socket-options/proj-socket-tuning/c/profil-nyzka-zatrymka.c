long sock_bdp_bytes(double mbit_per_s, double rtt_ms)
{
    double bytes_per_s = mbit_per_s * 1e6 / 8.0;
    return (long)(bytes_per_s * (rtt_ms / 1000.0));
}

static long clampl(long v, long lo, long hi)
{
    return v < lo ? lo : (v > hi ? hi : v);
}

int sock_apply_profile(int fd, sock_profile p, const sock_link *link,
                       sock_report *rep)
{
    memset(rep, 0, sizeof *rep);
    rep->too_late = is_connected(fd) || is_listening(fd);

    int bad = 0;
    long bdp = link ? sock_bdp_bytes(link->mbit_per_s, link->rtt_ms) : 0;

    if (p == SOCK_PROFILE_LATENCY) {
        /* 1. Не притримувати дрібне. Дванадцять байтів команди мусять вилетіти
              негайно, а не чекати підтвердження попереднього запису. */
        bad += set_int(fd, IPPROTO_TCP, TCP_NODELAY, 1, "TCP_NODELAY", rep);

        /* 2. Коротка черга. Байт, що вже лежить у передавальному буфері, не
              обігнати: чим довша черга, тим довше чекатиме команда «стоп»,
              записана після пачки телеметрії. «Малий» тут означає не
              «якнайменший», а «розміром приблизно з один обіг». */
        if (link && !rep->too_late) {
            int q = (int)clampl(bdp, 16 * 1024, 128 * 1024);
            bad += set_int(fd, SOL_SOCKET, SO_SNDBUF, q, "SO_SNDBUF", rep);
            bad += set_int(fd, SOL_SOCKET, SO_RCVBUF, q, "SO_RCVBUF", rep);
        }

        /* 3. Жоден виклик не висить довше за пів секунди — керування має
              повертатися до нашого коду, а не губитися в ядрі. */
        bad += set_tv(fd, SO_RCVTIMEO, 500, "SO_RCVTIMEO", rep);
        bad += set_tv(fd, SO_SNDTIMEO, 500, "SO_SNDTIMEO", rep);

        /* 4. З'єднання, у якому дані п'ять секунд не підтверджуються, мертве.
              Хай ядро розірве його само — краще чесна помилка, ніж тиша. */
        bad += set_int(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, 5000,
                       "TCP_USER_TIMEOUT", rep);

        /* 5. Мовчазне з'єднання перевіряємо зондами: 20 + 3·5 = 35 секунд до
              вироку. Заодно запис у трансляторі адрес не встигає протухнути. */
        bad += set_int(fd, SOL_SOCKET,  SO_KEEPALIVE,  1, "SO_KEEPALIVE",  rep);
        bad += set_int(fd, IPPROTO_TCP, TCP_KEEPIDLE, 20, "TCP_KEEPIDLE",  rep);
        bad += set_int(fd, IPPROTO_TCP, TCP_KEEPINTVL, 5, "TCP_KEEPINTVL", rep);
        bad += set_int(fd, IPPROTO_TCP, TCP_KEEPCNT,   3, "TCP_KEEPCNT",   rep);
    } else {
        /* Притримування НЕ чіпаємо: у великому потоці кожен запис і так повний,
           а дрібні хвости алгоритм склеїть — це чиста вигода. */
        if (link && !rep->too_late) {
            /* Подвійний запас: за один обіг вікно встигає підрости, а
               підтвердження приходять нерівно. */
            int q = (int)clampl(bdp * 2, 64 * 1024, 8L * 1024 * 1024);
            bad += set_int(fd, SOL_SOCKET, SO_SNDBUF, q, "SO_SNDBUF", rep);
            bad += set_int(fd, SOL_SOCKET, SO_RCVBUF, q, "SO_RCVBUF", rep);
        }
        bad += set_tv(fd, SO_RCVTIMEO, 30000, "SO_RCVTIMEO", rep);
        bad += set_tv(fd, SO_SNDTIMEO, 30000, "SO_SNDTIMEO", rep);
        bad += set_int(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, 60000,
                       "TCP_USER_TIMEOUT", rep);
    }
    return bad ? -1 : 0;
}
