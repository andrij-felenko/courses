#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/fanotify.h>
#include <sys/stat.h>

#define BUF_SIZE 4096

static void handle_perm_event(int fanotify_fd, const struct fanotify_event_metadata *e) {
    struct fanotify_response resp;
    resp.fd = e->fd;
    resp.response = FAN_ALLOW;

    /* Пастка 1: Ігноруємо операції самого демона, щоб уникнути взаємного блокування */
    if (e->pid == getpid()) {
        write(fanotify_fd, &resp, sizeof(resp));
        close(e->fd);
        return;
    }

    /* Аналізуємо файл за допомогою дескриптора, відданого ядром */
    char magic[4] = {0};
    ssize_t bytes_read = pread(e->fd, magic, sizeof(magic), 0);

    /* Забороняємо виконання файлів, якщо вони починаються з сигнатури небезпечного скрипту */
    if (bytes_read >= 4 && magic[0] == 'B' && magic[1] == 'A' && magic[2] == 'D' && magic[3] == '!') {
        printf("[GUARD] БЛОКУВАННЯ: Процес PID=%d намагався відкрити заборонений файл (FD=%d)\n",
               e->pid, e->fd);
        resp.response = FAN_DENY;
    } else {
        printf("[GUARD] ДОЗВОЛЕНО: Процес PID=%d відкрив файл (FD=%d)\n", e->pid, e->fd);
        resp.response = FAN_ALLOW;
    }

    /* Надсилаємо вердикт ядру */
    if (write(fanotify_fd, &resp, sizeof(resp)) < 0) {
        perror("write(fanotify_response)");
    }

    /* Обов'язково закриваємо файловий дескриптор події */
    close(e->fd);
}

int main(int argc, char *argv[]) {
    const char *target_path = (argc > 1) ? argv[1] : "/tmp";

    /* Ініціалізація групи fanotify з класом перевірки вмісту */
    int fanotify_fd = fanotify_init(FAN_CLASS_CONTENT | FAN_CLOEXEC, O_RDONLY | O_CLOEXEC);
    if (fanotify_fd < 0) {
        perror("fanotify_init");
        return 1;
    }

    /* Ставимо мітку перехоплення відкриття та виконання на вказаний шлях */
    if (fanotify_mark(fanotify_fd, FAN_MARK_ADD | FAN_MARK_MOUNT,
                      FAN_OPEN_PERM | FAN_OPEN_EXEC_PERM,
                      AT_FDCWD, target_path) < 0) {
        perror("fanotify_mark");
        close(fanotify_fd);
        return 1;
    }

    printf("[GUARD] Демон запущено. Перехоплення FAN_OPEN_PERM на %s...\n", target_path);

    /* Буфер для читання подій, вирівняний по межі метаданих */
    char buf[BUF_SIZE] __attribute__((aligned(__alignof__(struct fanotify_event_metadata))));

    for (;;) {
        ssize_t len = read(fanotify_fd, buf, sizeof(buf));
        if (len < 0) {
            if (errno == EINTR) continue;
            perror("read(fanotify_fd)");
            break;
        }

        const struct fanotify_event_metadata *metadata = (const struct fanotify_event_metadata *)buf;
        while (FAN_EVENT_OK(metadata, len)) {
            if (metadata->vers != FANOTIFY_METADATA_VERSION) {
                fprintf(stderr, "Невідповідність версії метаданих fanotify!\n");
                close(fanotify_fd);
                return 1;
            }

            if (metadata->mask & (FAN_OPEN_PERM | FAN_OPEN_EXEC_PERM)) {
                handle_perm_event(fanotify_fd, metadata);
            }

            metadata = FAN_EVENT_NEXT(metadata, len);
        }
    }

    close(fanotify_fd);
    return 0;
}
