#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#define TRACE_PIPE_PATH "/sys/kernel/tracing/trace_pipe"
#define BUFFER_SIZE 4096

int main(void)
{
    /*
     * Відкриття файлу trace_pipe у режимі лише для читання.
     * Потребує привілеїв root або належності до групи tracing.
     */
    int fd = open(TRACE_PIPE_PATH, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", TRACE_PIPE_PATH, strerror(errno));
        fprintf(stderr, "Перевірте права суперкористувача (sudo).\n");
        return EXIT_FAILURE;
    }

    printf("=== Потокове зчитування tracefs (%s) ===\n", TRACE_PIPE_PATH);
    printf("Натисніть Ctrl+C для зупинки.\n\n");

    char buffer[BUFFER_SIZE];
    ssize_t bytes_read;

    /*
     * Цикл потокового зчитування.
     * Системний виклик read() блокує процес до появи нових подій у ядрі.
     * Якщо блокування перервав сигнал, read() віддає -1 і errno == EINTR:
     * це не збій вводу-виводу, а привід просто повторити спробу.
     */
    for (;;) {
        bytes_read = read(fd, buffer, sizeof(buffer) - 1);

        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            fputs(buffer, stdout);
            fflush(stdout);
            continue;
        }
        if (bytes_read == 0)
            break;              /* кінець потоку */
        if (errno == EINTR)
            continue;           /* перервано сигналом — читаємо далі */

        fprintf(stderr, "Помилка читання з файлу: %s\n", strerror(errno));
        close(fd);
        return EXIT_FAILURE;
    }

    close(fd);
    return EXIT_SUCCESS;
}
