/* userspace_suspend.c: безпечний перехід у сон без втрати подій */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

int trigger_safe_suspend(void)
{
    char count_buf[64];
    int count_fd, state_fd;
    ssize_t bytes_read, bytes_written;

    /* Крок 1. Читаємо поточну кількість подій пробудження */
    count_fd = open("/sys/power/wakeup_count", O_RDWR);
    if (count_fd < 0) {
        perror("Не вдалося відкрити /sys/power/wakeup_count");
        return -errno;
    }

    bytes_read = read(count_fd, count_buf, sizeof(count_buf) - 1);
    if (bytes_read <= 0) {
        perror("Помилка читання лічильника подій");
        close(count_fd);
        return -EIO;
    }
    count_buf[bytes_read] = '\0';

    /* Крок 2. Атомарно записуємо зчитане значення назад у файл */
    lseek(count_fd, 0, SEEK_SET);
    bytes_written = write(count_fd, count_buf, strlen(count_buf));
    if (bytes_written < 0) {
        if (errno == EINVAL) {
            fprintf(stderr, "Подію пробудження зафіксовано перед сном! Призупинення скасовано.\n");
        } else {
            perror("Помилка запису в wakeup_count");
        }
        close(count_fd);
        return -errno;
    }
    close(count_fd);

    /* Крок 3. Ініціюємо перехід у сон */
    state_fd = open("/sys/power/state", O_WRONLY);
    if (state_fd < 0) {
        perror("Не вдалося відкрити /sys/power/state");
        return -errno;
    }

    printf("Перевірка успішна. Перехід у стан сну mem...\n");
    if (write(state_fd, "mem\n", 4) < 0) {
        perror("Помилка під час переходу в сон");
        close(state_fd);
        return -errno;
    }

    close(state_fd);
    printf("Система успішно прокинулася зі стану сну.\n");
    return 0;
}

int main(void)
{
    return trigger_safe_suspend() == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
