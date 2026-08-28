#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <pwd.h>
#include <errno.h>
#include <limits.h>

typedef enum {
    XDG_CAT_CONFIG,
    XDG_CAT_DATA,
    XDG_CAT_STATE,
    XDG_CAT_CACHE,
    XDG_CAT_RUNTIME
} xdg_category_t;

/* Отримання домашнього каталогу користувача із резервним запитом getpwuid */
static const char *get_user_home(void) {
    const char *home = getenv("HOME");
    if (home && home[0] != '\0') {
        return home;
    }
    struct passwd *pw = getpwuid(getuid());
    if (pw && pw->pw_dir && pw->pw_dir[0] != '\0') {
        return pw->pw_dir;
    }
    return NULL;
}

/* Обчислення абсолютного шляху каталогу XDG для застосунку */
int xdg_resolve_path(xdg_category_t cat, const char *app_name, char *out_buf, size_t out_len) {
    if (!app_name || app_name[0] == '\0' || !out_buf || out_len == 0) {
        errno = EINVAL;
        return -1;
    }

    const char *env_var = NULL;
    const char *default_rel = NULL;

    switch (cat) {
        case XDG_CAT_CONFIG:
            env_var = getenv("XDG_CONFIG_HOME");
            default_rel = ".config";
            break;
        case XDG_CAT_DATA:
            env_var = getenv("XDG_DATA_HOME");
            default_rel = ".local/share";
            break;
        case XDG_CAT_STATE:
            env_var = getenv("XDG_STATE_HOME");
            default_rel = ".local/state";
            break;
        case XDG_CAT_CACHE:
            env_var = getenv("XDG_CACHE_HOME");
            default_rel = ".cache";
            break;
        case XDG_CAT_RUNTIME:
            env_var = getenv("XDG_RUNTIME_DIR");
            default_rel = NULL;
            break;
        default:
            errno = EINVAL;
            return -1;
    }

    /* Якщо змінна задана і містить АБСОЛЮТНИЙ шлях (починається зі слеша '/') */
    if (env_var && env_var[0] == '/') {
        int ret = snprintf(out_buf, out_len, "%s/%s", env_var, app_name);
        return (ret >= 0 && (size_t)ret < out_len) ? 0 : -1;
    }

    /* Для RUNTIME відсутність змінної — помилка середовища виконання */
    if (cat == XDG_CAT_RUNTIME) {
        errno = ENOENT;
        return -1;
    }

    /* Fallback до $HOME/<default_rel>/<app_name> */
    const char *home = get_user_home();
    if (!home) {
        errno = ENOENT;
        return -1;
    }

    int ret = snprintf(out_buf, out_len, "%s/%s/%s", home, default_rel, app_name);
    return (ret >= 0 && (size_t)ret < out_len) ? 0 : -1;
}

/* Рекурсивне створення дерева каталогів із перевіркою прав (аналог mkdir -p) */
int xdg_mkdir_p(const char *path, mode_t mode) {
    if (!path || path[0] == '\0') {
        errno = EINVAL;
        return -1;
    }

    char tmp[PATH_MAX];
    size_t len = strnlen(path, sizeof(tmp));
    if (len >= sizeof(tmp)) {
        errno = ENAMETOOLONG;
        return -1;
    }
    memcpy(tmp, path, len + 1);

    for (char *p = tmp + 1; *p; p++) {
        if (*p == '/') {
            *p = '\0';
            if (mkdir(tmp, mode) != 0) {
                if (errno != EEXIST) {
                    return -1;
                }
            }
            *p = '/';
        }
    }
    if (mkdir(tmp, mode) != 0) {
        if (errno != EEXIST) {
            return -1;
        }
    }
    return 0;
}

/* Отримання шляху батьківського каталогу */
static int get_parent_dir(const char *file_path, char *dir_buf, size_t dir_len) {
    const char *last_slash = strrchr(file_path, '/');
    if (!last_slash) {
        if (dir_len < 2) return -1;
        dir_buf[0] = '.';
        dir_buf[1] = '\0';
        return 0;
    }
    size_t len = (last_slash == file_path) ? 1 : (size_t)(last_slash - file_path);
    if (len >= dir_len) return -1;
    memcpy(dir_buf, file_path, len);
    dir_buf[len] = '\0';
    return 0;
}

/* Атомарний запис конфігураційного файлу через mkstemp, fsync та rename */
int xdg_atomic_write_file(const char *dest_path, const void *data, size_t size, mode_t mode) {
    if (!dest_path || (!data && size > 0)) {
        errno = EINVAL;
        return -1;
    }

    char dir_path[PATH_MAX];
    if (get_parent_dir(dest_path, dir_path, sizeof(dir_path)) != 0) {
        errno = ENAMETOOLONG;
        return -1;
    }

    /* Гарантуємо існування батьківського каталогу */
    if (xdg_mkdir_p(dir_path, 0700) != 0) {
        return -1;
    }

    /* Створюємо тимчасовий файл у ТОМУ САМОМУ каталозі (уникнення помилки EXDEV) */
    char temp_path[PATH_MAX];
    int ret = snprintf(temp_path, sizeof(temp_path), "%s/tmp.XXXXXX", dir_path);
    if (ret < 0 || (size_t)ret >= sizeof(temp_path)) {
        errno = ENAMETOOLONG;
        return -1;
    }

    int fd = mkstemp(temp_path);
    if (fd < 0) {
        return -1;
    }

    /* Встановлюємо безпечні права доступу на створений файл */
    if (fchmod(fd, mode) != 0) {
        close(fd);
        unlink(temp_path);
        return -1;
    }

    /* Надійний повнорозмірний запис у буфер */
    const char *ptr = (const char *)data;
    size_t remaining = size;
    while (remaining > 0) {
        ssize_t written = write(fd, ptr, remaining);
        if (written < 0) {
            if (errno == EINTR) continue;
            close(fd);
            unlink(temp_path);
            return -1;
        }
        ptr += written;
        remaining -= (size_t)written;
    }

    /* 1. Синхронізація сторінок пам'яті файлу на фізичний носій */
    if (fsync(fd) != 0) {
        close(fd);
        unlink(temp_path);
        return -1;
    }

    if (close(fd) != 0) {
        unlink(temp_path);
        return -1;
    }

    /* 2. Атомарна заміна старого файлу новим у записі каталогу */
    if (rename(temp_path, dest_path) != 0) {
        unlink(temp_path);
        return -1;
    }

    /* 3. Синхронізація метаданих самого каталогу */
    int dir_fd = open(dir_path, O_RDONLY | O_DIRECTORY);
    if (dir_fd >= 0) {
        fsync(dir_fd);
        close(dir_fd);
    }

    return 0;
}

int main(void) {
    const char *app = "demo_service";
    char conf_dir[PATH_MAX];
    char cache_dir[PATH_MAX];

    if (xdg_resolve_path(XDG_CAT_CONFIG, app, conf_dir, sizeof(conf_dir)) == 0) {
        printf("Конфігураційний каталог: %s\n", conf_dir);
    }
    if (xdg_resolve_path(XDG_CAT_CACHE, app, cache_dir, sizeof(cache_dir)) == 0) {
        printf("Каталог кешу:             %s\n", cache_dir);
    }

    /* Збереження налаштувань через атомарний запис */
    char conf_file[PATH_MAX];
    snprintf(conf_file, sizeof(conf_file), "%s/settings.json", conf_dir);
    const char *json_payload = "{\n  \"version\": 1,\n  \"theme\": \"dark\"\n}\n";

    if (xdg_atomic_write_file(conf_file, json_payload, strlen(json_payload), 0600) == 0) {
        printf("Успішно збережено конфігурацію в %s\n", conf_file);
    } else {
        perror("Помилка збереження");
        return 1;
    }

    return 0;
}
