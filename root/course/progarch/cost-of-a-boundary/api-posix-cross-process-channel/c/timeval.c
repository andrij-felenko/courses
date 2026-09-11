#include <sys/socket.h>
#include <sys/time.h>
#include <stdio.h>

// Встановлення таймаутів на передачу та прийом через сокетний канал
int configure_channel_timeouts(int sockfd, int timeout_seconds) {
    struct timeval tv;
    tv.tv_sec = timeout_seconds;
    tv.tv_usec = 0;

    // Встановлюємо таймаут на прийом
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
        perror("Не вдалося встановити SO_RCVTIMEO");
        return -1;
    }

    // Встановлюємо таймаут на відправку
    if (setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv)) < 0) {
        perror("Не вдалося встановити SO_SNDTIMEO");
        return -1;
    }

    return 0;
}
