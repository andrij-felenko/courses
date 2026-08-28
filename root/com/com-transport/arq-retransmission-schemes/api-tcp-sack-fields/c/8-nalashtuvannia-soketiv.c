#include <stdio.h>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <netinet/in.h>

/* Налаштування сокета для мінімізації затримок ARQ у мовах C */
int configure_low_latency_socket(int sockfd) {
    int enable = 1;

    /* 1. Вимикаємо буферизацію Нагла */
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &enable, sizeof(enable)) != 0) {
        return -1;
    }

    /* 2. Вмикаємо негайну генерацію ACK (без затримки 40 мс) */
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_QUICKACK, &enable, sizeof(enable)) != 0) {
        return -1;
    }

    /* 3. Встановлюємо таймаут непідтверджених даних 1500 мс (замість 2 хв) */
    unsigned int user_timeout_ms = 1500;
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_USER_TIMEOUT, &user_timeout_ms, sizeof(user_timeout_ms)) != 0) {
        return -1;
    }

    return 0;
}
