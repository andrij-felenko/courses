/* hook_write.c — Перехоплення функції write() мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>

/* Сигнатура оригінальної функції write */
typedef ssize_t (*real_write_t)(int fd, const void *buf, size_t count);

ssize_t write(int fd, const void *buf, size_t count) {
    /* 1. Пошук оригінальної функції write у libc за допомогою RTLD_NEXT */
    static real_write_t real_write = NULL;
    if (!real_write) {
        real_write = (real_write_t)dlsym(RTLD_NEXT, "write");
        if (!real_write) {
            char msg[] = "[HOOK] Помилка: не вдалося знайти справжній write\n";
            (void)::write(STDERR_FILENO, msg, sizeof(msg) - 1);
            return -1;
        }
    }

    /* 2. Власна логіка перехоплювача: виводимо лог для stdout (1) та stderr (2) */
    if (fd == STDOUT_FILENO || fd == STDERR_FILENO) {
        char log_buf[128];
        int log_len = snprintf(log_buf, sizeof(log_buf),
                               "[PRELOAD HOOK] Перехоплено write(fd=%d, count=%zu bytes)\n",
                               fd, count);
        if (log_len > 0) {
            /* Викликаємо справжній write для виводу логу у stderr */
            real_write(STDERR_FILENO, log_buf, (size_t)log_len);
        }
    }

    /* 3. Передаємо виконання оригінальній функції write у libc */
    return real_write(fd, buf, count);
}
