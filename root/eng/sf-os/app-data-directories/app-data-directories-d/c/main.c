#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <pwd.h>
#include <errno.h>
#include <limits.h>

/* Отримання абсолютного шляху конфігураційного каталогу */
int get_app_config_dir(const char *app_name, char *out_path, size_t max_len) {
    if (!app_name || !out_path || max_len == 0) {
        errno = EINVAL;
        return -1;
    }

    const char *xdg_config = getenv("XDG_CONFIG_HOME");
    if (xdg_config && xdg_config[0] == '/') {
        int n = snprintf(out_path, max_len, "%s/%s", xdg_config, app_name);
        return (n > 0 && (size_t)n < max_len) ? 0 : -1;
    }

    const char *home = getenv("HOME");
    if (!home || home[0] == '\0') {
        struct passwd *pw = getpwuid(getuid());
        if (!pw || !pw->pw_dir) {
            errno = ENOENT;
            return -1;
        }
        home = pw->pw_dir;
    }

    int n = snprintf(out_path, max_len, "%s/.config/%s", home, app_name);
    return (n > 0 && (size_t)n < max_len) ? 0 : -1;
}

/* Атомарний запис конфігураційного файлу */
int save_config_atomic(const char *file_path, const char *content, size_t len) {
    char dir_path[PATH_MAX];
    char temp_path[PATH_MAX];

    /* Виокремлюємо батьківський каталог */
    const char *last_slash = strrchr(file_path, '/');
    if (!last_slash) return -1;
    
    size_t dlen = (size_t)(last_slash - file_path);
    if (dlen >= sizeof(dir_path)) return -1;
    memcpy(dir_path, file_path, dlen);
    dir_path[dlen] = '\0';

    /* Формуємо шаблон для mkstemp у тому самому каталозі */
    snprintf(temp_path, sizeof(temp_path), "%s/cfg.XXXXXX", dir_path);
    int fd = mkstemp(temp_path);
    if (fd < 0) return -1;

    /* Обмежуємо права: лише читання/запис власнику */
    fchmod(fd, 0600);

    /* Запис даних */
    size_t written = 0;
    while (written < len) {
        ssize_t res = write(fd, content + written, len - written);
        if (res < 0) {
            if (errno == EINTR) continue;
            close(fd);
            unlink(temp_path);
            return -1;
        }
        written += (size_t)res;
    }

    /* Скидання сторінок пам'яті на диск */
    if (fsync(fd) != 0) {
        close(fd);
        unlink(temp_path);
        return -1;
    }
    close(fd);

    /* Атомарна підміна імені */
    if (rename(temp_path, file_path) != 0) {
        unlink(temp_path);
        return -1;
    }

    /* Синхронізація батьківського каталогу */
    int dir_fd = open(dir_path, O_RDONLY | O_DIRECTORY);
    if (dir_fd >= 0) {
        fsync(dir_fd);
        close(dir_fd);
    }
    return 0;
}
