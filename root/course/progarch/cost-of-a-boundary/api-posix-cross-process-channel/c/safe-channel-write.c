#define _GNU_SOURCE
#include <sys/socket.h>
#include <errno.h>
#include <stdio.h>
#include <unistd.h>

// Безпечна відправка повідомлення з гарантованим захистом від SIGPIPE
int safe_channel_write(int channel_fd, const void *buf, size_t len) {
    while (1) {
        // Прапорець MSG_NOSIGNAL захищає від генерації вбивчого сигналу SIGPIPE
        ssize_t sent = send(channel_fd, buf, len, MSG_NOSIGNAL);
        if (sent >= 0) {
            return (size_t)sent == len ? 0 : -1;
        }

        if (errno == EINTR) {
            continue; // Системний виклик перервано зовнішнім сигналом — повторюємо
        }
        if (errno == EPIPE || errno == ECONNRESET) {
            fprintf(stderr, "Протилежний процес розірвав з'єднання або аварійно впав\n");
            return -1;
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            fprintf(stderr, "Вичерпано сокетний таймаут передачі\n");
            return -1;
        }

        perror("Невідома системна помилка сокета");
        return -1;
    }
}
