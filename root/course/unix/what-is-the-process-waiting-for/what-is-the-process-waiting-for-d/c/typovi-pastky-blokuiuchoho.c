#include <sys/socket.h>
#include <sys/time.h>
#include <stdio.h>
#include <unistd.h>

int configure_socket_timeouts(int sockfd, int timeout_seconds) {
    struct timeval tv;
    tv.tv_sec = timeout_seconds;
    tv.tv_usec = 0;

    // Встановлюємо таймаут на операції читання
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
        perror("Помилка налаштування SO_RCVTIMEO");
        return -1;
    }

    // Встановлюємо таймаут на операції запису
    if (setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv)) < 0) {
        perror("Помилка налаштування SO_SNDTIMEO");
        return -1;
    }

    return 0;
}
