#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <errno.h>
#include <stdbool.h>

#define KMSG_PATH "/dev/kmsg"
#define BUF_SIZE 8192

static const char *loglevel_to_string(int level) {
    switch (level & 0x07) {
        case 0: return "EMERG";
        case 1: return "ALERT";
        case 2: return "CRIT";
        case 3: return "ERR";
        case 4: return "WARN";
        case 5: return "NOTICE";
        case 6: return "INFO";
        case 7: return "DEBUG";
        default: return "UNK";
    }
}

static void parse_and_print_record(const char *buf, ssize_t len) {
    int level = 0;
    unsigned long long seq = 0;
    unsigned long long nsec = 0;
    char flags = '-';
    char message[4096] = {0};
    char subsystem[128] = "kernel";

    /* Шукаємо розділювач крапки з комою між заголовком та повідомленням */
    const char *semicolon = memchr(buf, ';', len);
    if (!semicolon) {
        return;
    }

    /* Розбираємо заголовок: level,seq,nsec,flags; */
    if (sscanf(buf, "%d,%llu,%llu,%c", &level, &seq, &nsec, &flags) < 3) {
        return;
    }

    /* Знаходимо кінець першого рядка (тексту повідомлення) */
    const char *msg_start = semicolon + 1;
    const char *newline = memchr(msg_start, '\n', len - (msg_start - buf));
    size_t msg_len = newline ? (size_t)(newline - msg_start) : strlen(msg_start);
    if (msg_len >= sizeof(message)) {
        msg_len = sizeof(message) - 1;
    }
    memcpy(message, msg_start, msg_len);
    message[msg_len] = '\0';

    /* Шукаємо словник метаданих у наступних рядках (наприклад, SUBSYSTEM=net) */
    if (newline && (size_t)(newline - buf) < (size_t)len) {
        const char *subsys_ptr = strstr(newline, " SUBSYSTEM=");
        if (subsys_ptr) {
            subsys_ptr += 11; /* Пропускаємо " SUBSYSTEM=" */
            const char *subsys_end = strchr(subsys_ptr, '\n');
            size_t subsys_len = subsys_end ? (size_t)(subsys_end - subsys_ptr) : strlen(subsys_ptr);
            if (subsys_len >= sizeof(subsystem)) {
                subsys_len = sizeof(subsystem) - 1;
            }
            memcpy(subsystem, subsys_ptr, subsys_len);
            subsystem[subsys_len] = '\0';
        }
    }

    double seconds = (double)nsec / 1000000000.0;
    printf("[%12.6f] [%-6s] [%-10s] (seq=%llu): %s\n",
           seconds, loglevel_to_string(level), subsystem, seq, message);
}

int main(void) {
    int fd = open(KMSG_PATH, O_RDWR | O_NONBLOCK);
    if (fd < 0) {
        perror("Failed to open " KMSG_PATH);
        return EXIT_FAILURE;
    }

    /* Зсуваємо позицію читача на кінець буфера, щоб бачити лише нові події */
    if (lseek(fd, 0, SEEK_END) < 0) {
        perror("Failed to lseek SEEK_END on " KMSG_PATH);
        close(fd);
        return EXIT_FAILURE;
    }

    /* Записуємо тестове повідомлення з простору користувача у журнал ядра */
    const char *hello_msg = "<6>kmsg_watcher: watcher daemon initialized successfully\n";
    if (write(fd, hello_msg, strlen(hello_msg)) < 0) {
        perror("Failed to write to " KMSG_PATH);
    }

    printf("Listening for new kernel messages on %s...\n", KMSG_PATH);

    struct pollfd pfd = {
        .fd = fd,
        .events = POLLIN
    };

    char buffer[BUF_SIZE];

    while (1) {
        int ret = poll(&pfd, 1, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            perror("poll failed");
            break;
        }

        if (pfd.revents & POLLIN) {
            while (1) {
                ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
                if (bytes_read < 0) {
                    if (errno == EAGAIN || errno == EWOULDBLOCK) {
                        break; /* Немає більше нових даних */
                    }
                    if (errno == EPIPE) {
                        fprintf(stderr, "WARN: Kernel log buffer overwritten, messages lost!\n");
                        continue; /* Автоматично перестрибуємо на доступні дані */
                    }
                    perror("read failed");
                    goto cleanup;
                }

                buffer[bytes_read] = '\0';
                parse_and_print_record(buffer, bytes_read);
            }
        }
    }

cleanup:
    close(fd);
    return EXIT_SUCCESS;
}
