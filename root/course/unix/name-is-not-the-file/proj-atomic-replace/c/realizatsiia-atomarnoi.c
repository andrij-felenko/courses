#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <libgen.h>

/* Безпечний атомарний запис буфера даних у цільовий файл */
int atomic_write_file(const char *target_path, const void *data, size_t size, mode_t default_mode) {
    char dir_buf[1024];
    char temp_path[1024];
    struct stat st;
    mode_t target_mode = default_mode;
    uid_t target_uid = (uid_t)-1;
    gid_t target_gid = (gid_t)-1;
    int has_original = 0;

    if (!target_path || !data) {
        errno = EINVAL;
        return -1;
    }

    /* Отримуємо шлях до каталогу цільового файлу */
    strncpy(dir_buf, target_path, sizeof(dir_buf) - 1);
    dir_buf[sizeof(dir_buf) - 1] = '\0';
    char *dir_name = dirname(dir_buf);

    /* Якщо цільовий файл уже існує, зчитуємо його права та власника */
    if (stat(target_path, &st) == 0) {
        target_mode = st.st_mode & 07777;
        target_uid = st.st_uid;
        target_gid = st.st_gid;
        has_original = 1;
    }

    /* Формуємо унікальний шлях до тимчасового файлу поруч із цільовим */
    snprintf(temp_path, sizeof(temp_path), "%s/.tmp_atomic_%d_%lu", dir_name, (int)getpid(), (unsigned long)size);

    /* Створюємо новий інод з обов'язковою перевіркою відсутності колізій */
    int fd = open(temp_path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, target_mode);
    if (fd < 0) {
        return -1;
    }

    /* Якщо запускаємося від привілейованого користувача, відновлюємо UID/GID */
    if (has_original && geteuid() == 0) {
        if (fchown(fd, target_uid, target_gid) < 0) {
            int err = errno;
            close(fd);
            unlink(temp_path);
            errno = err;
            return -1;
        }
    }

    /* Повний запис даних з обов'язковим врахуванням часткових записів та сигналів */
    const char *ptr = (const char *)data;
    size_t remaining = size;
    while (remaining > 0) {
        ssize_t written = write(fd, ptr, remaining);
        if (written < 0) {
            if (errno == EINTR) continue;
            int err = errno;
            close(fd);
            unlink(temp_path);
            errno = err;
            return -1;
        }
        ptr += written;
        remaining -= (size_t)written;
    }

    /* Примусово вимиваємо сторінки кешу та метадані інода на диск */
    if (fsync(fd) < 0) {
        int err = errno;
        close(fd);
        unlink(temp_path);
        errno = err;
        return -1;
    }

    /* Закриваємо дескриптор перед фінальною операцією підміни */
    if (close(fd) < 0) {
        int err = errno;
        unlink(temp_path);
        errno = err;
        return -1;
    }

    /* Атомарно замінюємо ім'я файлу на новий інод */
    if (rename(temp_path, target_path) < 0) {
        int err = errno;
        unlink(temp_path);
        errno = err;
        return -1;
    }

    /* Фіксуємо змінений запис каталогу на накопичувачі */
    int dir_fd = open(dir_name, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (dir_fd >= 0) {
        fsync(dir_fd);
        close(dir_fd);
    }

    return 0;
}
