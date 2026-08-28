#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <signal.h>
#include <errno.h>
#include <time.h>

#define FIFO_PATH "/tmp/app_events.fifo"
#define MAX_MSG_SIZE 512 /* Значно менше PIPE_BUF (4096), тому запис строго атомарний */

/* Запуск демона-читача логів */
void run_server(void) {
    /* Створюємо FIFO з правами rw-rw-rw- */
    unlink(FIFO_PATH);
    if (mkfifo(FIFO_PATH, 0666) < 0 && errno != EEXIST) {
        perror("mkfifo");
        exit(EXIT_FAILURE);
    }

    printf("[Сервер] FIFO створено: %s\n", FIFO_PATH);

    /* Трюк O_RDWR: утримуємо лічильник письменників >= 1, щоб read не крутився в 0 (EOF) */
    int fifo_fd = open(FIFO_PATH, O_RDWR);
    if (fifo_fd < 0) {
        perror("open server FIFO");
        exit(EXIT_FAILURE);
    }

    printf("[Сервер] Очікування повідомлень від клієнтів...\n");

    char buffer[MAX_MSG_SIZE];
    while (1) {
        ssize_t bytes_read = read(fifo_fd, buffer, sizeof(buffer) - 1);
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            printf("[Отримано подію] %s", buffer);
            fflush(stdout);
        } else if (bytes_read < 0) {
            if (errno == EINTR) continue;
            perror("read error");
            break;
        }
    }

    close(fifo_fd);
    unlink(FIFO_PATH);
}

/* Відправка події від клієнта */
int send_log_event(const char *service_name, const char *message) {
    /* Відкриваємо з O_NONBLOCK: якщо сервер не слухає, дістанемо ENXIO негайно */
    int fd = open(FIFO_PATH, O_WRONLY | O_NONBLOCK);
    if (fd < 0) {
        if (errno == ENXIO) {
            fprintf(stderr, "[Клієнт %s] Помилка: Сервер логів не запущений (немає читача).\n", service_name);
        } else {
            perror("open client FIFO");
        }
        return -1;
    }

    char record[MAX_MSG_SIZE];
    time_t now = time(NULL);
    struct tm tm_buf;
    localtime_r(&now, &tm_buf);

    char time_str[32];
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", &tm_buf);

    int len = snprintf(record, sizeof(record), "[%s] [%s (PID:%d)]: %s\n",
                       time_str, service_name, getpid(), message);

    if (len > 0) {
        /* Ігноруємо SIGPIPE, щоб процес не загинув при раптовому закритті сервера */
        struct sigaction sa;
        memset(&sa, 0, sizeof(sa));
        sa.sa_handler = SIG_IGN;
        sigaction(SIGPIPE, &sa, NULL);

        ssize_t written = write(fd, record, (size_t)len);
        if (written < 0) {
            if (errno == EPIPE) {
                fprintf(stderr, "[Клієнт %s] Помилка: Канал зламано (EPIPE).\n", service_name);
            } else {
                perror("write client");
            }
            close(fd);
            return -1;
        }
    }

    close(fd);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc > 1 && strcmp(argv[1], "server") == 0) {
        run_server();
    } else if (argc > 3 && strcmp(argv[1], "client") == 0) {
        send_log_event(argv[2], argv[3]);
    } else {
        printf("Використання:\n");
        printf("  %s server                  — запустити фоновий збирач логів\n", argv[0]);
        printf("  %s client <сервіс> <текст> — надіслати подію в іменований канал\n", argv[0]);
    }
    return 0;
}
