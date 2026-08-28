int enable_socket_safety_timeouts(int sockfd) {
    int keepalive = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(keepalive));

    int keepidle = 2;    /* Почати надсилати probe-пакети після 2 секунд тиші */
    setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPIDLE, &keepidle, sizeof(keepidle));

    int keepintvl = 1;   /* Інтервал між повторними probe-пакетами: 1 секунда */
    setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPINTVL, &keepintvl, sizeof(keepintvl));

    int keepcnt = 3;     /* Визнати сокет мертвим після 3 пропущених відповідей */
    setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPCNT, &keepcnt, sizeof(keepcnt));

    /* Граничний таймаут утримання непідтверджених даних у мілісекундах (Linux 2.6.37+) */
    unsigned int user_timeout_ms = 4000;
    setsockopt(sockfd, IPPROTO_TCP, TCP_USER_TIMEOUT, &user_timeout_ms, sizeof(user_timeout_ms));
    return 0;
}
