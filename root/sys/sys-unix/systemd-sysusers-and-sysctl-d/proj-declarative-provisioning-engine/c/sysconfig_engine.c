/* sysconfig_engine.c — C99 / POSIX реалізація рушія конфігурації */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <shadow.h>
#include <pwd.h>
#include <errno.h>

#define MAX_ENTRIES 256
#define MAX_PATH 512

typedef struct {
    char name[64];
    char full_path[MAX_PATH];
    int priority; /* 3: /etc, 2: /run, 1: /usr/lib */
    int is_masked;
} ConfigFile;

static int compare_files(const void *a, const void *b) {
    const ConfigFile *fa = (const ConfigFile *)a;
    const ConfigFile *fb = (const ConfigFile *)b;
    return strcmp(fa->name, fb->name);
}

/* Сканування ієрархії каталогів з дедуплікацією та затіненням */
int sc_scan_dir(const char *subdirs, ConfigFile *out_files, int *count) {
    const char *dirs[] = {"/etc", "/run", "/usr/lib"};
    int p_levels[] = {3, 2, 1};
    int total = 0;

    for (int i = 0; i < 3; i++) {
        char dir_path[MAX_PATH];
        snprintf(dir_path, sizeof(dir_path), "%s/%s", dirs[i], subdirs);

        DIR *d = opendir(dir_path);
        if (!d) continue;

        struct dirent *entry;
        while ((entry = readdir(d)) != NULL) {
            if (entry->d_type != DT_REG && entry->d_type != DT_LNK) continue;
            if (!strstr(entry->d_name, ".conf")) continue;

            /* Перевірка чи файл уже був доданий з вищим пріоритетом */
            int exists = 0;
            for (int j = 0; j < total; j++) {
                if (strcmp(out_files[j].name, entry->d_name) == 0) {
                    exists = 1;
                    break;
                }
            }
            if (exists) continue;

            ConfigFile *cf = &out_files[total];
            strncpy(cf->name, entry->d_name, sizeof(cf->name) - 1);
            snprintf(cf->full_path, sizeof(cf->full_path), "%s/%s", dir_path, entry->d_name);
            cf->priority = p_levels[i];

            /* Перевірка на маскування (/dev/null) */
            struct stat st;
            if (lstat(cf->full_path, &st) == 0 && S_ISLNK(st.st_mode)) {
                char target[MAX_PATH];
                ssize_t len = readlink(cf->full_path, target, sizeof(target) - 1);
                if (len > 0) {
                    target[len] = '\0';
                    if (strstr(target, "/dev/null")) cf->is_masked = 1;
                }
            }
            total++;
        }
        closedir(d);
    }

    qsort(out_files, total, sizeof(ConfigFile), compare_files);
    *count = total;
    return 0;
}

/* Застосування ключа sysctl у /proc/sys */
int sc_apply_sysctl_line(const char *key, const char *value) {
    char proc_path[MAX_PATH] = "/proc/sys/";
    int path_idx = strlen(proc_path);
    int ignore_error = 0;

    const char *k_ptr = key;
    if (k_ptr[0] == '-') {
        ignore_error = 1;
        k_ptr++;
    }

    for (int i = 0; k_ptr[i] != '\0'; i++) {
        if (k_ptr[i] == '.') {
            proc_path[path_idx++] = '/';
        } else {
            proc_path[path_idx++] = k_ptr[i];
        }
    }
    proc_path[path_idx] = '\0';

    int fd = open(proc_path, O_WRONLY);
    if (fd < 0) {
        if (ignore_error) return 0;
        fprintf(stderr, "Помилка відкриття sysctl %s: %s\n", proc_path, strerror(errno));
        return -1;
    }

    ssize_t w = write(fd, value, strlen(value));
    close(fd);
    return (w > 0) ? 0 : -1;
}

/* Додавання системного користувача з блокуванням lckpwdf */
int sc_apply_sysuser(const char *username, uid_t uid, const char *comment, const char *home, const char *shell) {
    if (lckpwdf() != 0) {
        fprintf(stderr, "Не вдалося заблокувати базу даних користувачів: %s\n", strerror(errno));
        return -1;
    }

    /* Перевірка чи існує користувач */
    if (getpwnam(username) != NULL) {
        ulckpwdf();
        return 0; /* Вже існує, ідемпотентний вихід */
    }

    FILE *f = fopen("/etc/passwd", "a");
    if (!f) {
        ulckpwdf();
        return -1;
    }

    fprintf(f, "%s:x:%u:%u:%s:%s:%s\n", username, (unsigned)uid, (unsigned)uid, comment, home, shell);
    fclose(f);

    ulckpwdf();
    return 0;
}
