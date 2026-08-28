#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <libgen.h>

// Атомарно зберігає буфер data розміром size у файл target_path
int atomic_save_file(const char *target_path, const void *data, size_t size) {
    if (!target_path || (!data && size > 0)) {
        return -1;
    }

    // 1. Зчитуємо права доступу оригіналу, якщо він існує
    mode_t target_mode = 0644;
    struct stat st;
    if (stat(target_path, &st) == 0) {
        target_mode = st.st_mode & 0777;
    }

    // 2. Формуємо шаблон тимчасового файлу в тому ж каталозі
    char tmp_path[4096];
    int len = snprintf(tmp_path, sizeof(tmp_path), "%s.tmp_XXXXXX", target_path);
    if (len < 0 || (size_t)len >= sizeof(tmp_path)) {
        errno = ENAMETOOLONG;
        return -1;
    }

    // 3. Створюємо унікальний тимчасовий файл
    int fd = mkstemp(tmp_path);
    if (fd < 0) {
        return -1;
    }

    // Встановлюємо права доступу
    if (fchmod(fd, target_mode) != 0) {
        int err = errno;
        close(fd);
        unlink(tmp_path);
        errno = err;
        return -1;
    }

    // 4. Записуємо всі дані в циклі з контролем помилок
    const char *buf = (const char *)data;
    size_t left = size;
    while (left > 0) {
        ssize_t n = write(fd, buf, left);
        if (n < 0) {
            if (errno == EINTR) continue; // Переривання системним сигналом
            int err = errno;
            close(fd);
            unlink(tmp_path);
            errno = err;
            return -1;
        }
        buf += n;
        left -= (size_t)n;
    }

    // 5. Примусово скидаємо брудні сторінки та інод на фізичний диск
    if (fsync(fd) != 0) {
        int err = errno;
        close(fd);
        unlink(tmp_path);
        errno = err;
        return -1;
    }

    // Закриваємо дескриптор файлу
    if (close(fd) != 0) {
        int err = errno;
        unlink(tmp_path);
        errno = err;
        return -1;
    }

    // 6. Атомарно замінюємо старий файл новим
    if (rename(tmp_path, target_path) != 0) {
        int err = errno;
        unlink(tmp_path);
        errno = err;
        return -1;
    }

    // 7. Скидаємо зміни метаданих батьківського каталогу
    char dir_buf[4096];
    strncpy(dir_buf, target_path, sizeof(dir_buf) - 1);
    dir_buf[sizeof(dir_buf) - 1] = '\0';
    char *dir_name = dirname(dir_buf);

    int dir_fd = open(dir_name, O_RDONLY | O_DIRECTORY);
    if (dir_fd >= 0) {
        fsync(dir_fd);
        close(dir_fd);
    }

    return 0;
}
