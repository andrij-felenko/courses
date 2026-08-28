#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <linux/input.h>

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/input/event0";
    int fd = open(dev_path, O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій введення");
        return 1;
    }

    printf("Відкрито %s. Читання подій (натисніть Ctrl+C для виходу)...\n", dev_path);

    struct input_event ev;
    while (1) {
        ssize_t bytes_read = read(fd, &ev, sizeof(ev));
        if (bytes_read < 0) {
            if (errno == EINTR) continue;
            perror("Помилка читання з evdev");
            break;
        }

        if (bytes_read != sizeof(ev)) {
            fprintf(stderr, "Прочитано некоректну кількість байтів: %zd\n", bytes_read);
            continue;
        }

        if (ev.type == EV_KEY) {
            printf("[KEY] Код: %3d, Значення: %d (%s)\n",
                   ev.code, ev.value,
                   ev.value == 1 ? "Натиснуто" : ev.value == 0 ? "Відпущено" : "Автоповтор");
        } else if (ev.type == EV_REL) {
            printf("[REL] Осi: %3d, Зсув: %d\n", ev.code, ev.value);
        } else if (ev.type == EV_ABS) {
            printf("[ABS] Осi: %3d, Значення: %d\n", ev.code, ev.value);
        } else if (ev.type == EV_SYN) {
            if (ev.code == SYN_REPORT) {
                printf("--- SYN_REPORT (Кінець фрейму) ---\n");
            } else if (ev.code == SYN_DROPPED) {
                printf("⚠️ УВАГА: SYN_DROPPED! Буфер переповнено.\n");
            }
        }
    }

    close(fd);
    return 0;
}
