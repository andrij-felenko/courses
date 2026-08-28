#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <errno.h>

typedef struct {
    const char *path;
    const char *expected_type;
    int is_symlink;
    char target_path[256];
    dev_t dev_id;
    int is_readonly;
} fhs_entry_info_t;

static int inspect_fhs_path(const char *path, fhs_entry_info_t *info) {
    struct stat st;
    struct statvfs stfs;
    ssize_t len;

    memset(info, 0, sizeof(*info));
    info->path = path;

    if (lstat(path, &st) != 0) {
        return -1;
    }

    info->dev_id = st.st_dev;

    if (S_ISLNK(st.st_mode)) {
        info->is_symlink = 1;
        len = readlink(path, info->target_path, sizeof(info->target_path) - 1);
        if (len != -1) {
            info->target_path[len] = '\0';
        } else {
            snprintf(info->target_path, sizeof(info->target_path), "<error>");
        }
    }

    if (statvfs(path, &stfs) == 0) {
        if (stfs.f_flag & ST_RDONLY) {
            info->is_readonly = 1;
        }
    }

    return 0;
}

static void print_fhs_report(const fhs_entry_info_t *info) {
    printf("Каталог: %-12s | ", info->path);
    if (info->is_symlink) {
        printf("Тип: SYMLINK -> %-12s | ", info->target_path);
    } else {
        printf("Тип: DIRECTORY           | ");
    }
    printf("DevID: 0x%-6lx | ", (unsigned long)info->dev_id);
    printf("Mode: %s\n", info->is_readonly ? "READ-ONLY" : "READ-WRITE");
}

int main(void) {
    const char *fhs_paths[] = {
        "/",
        "/bin",
        "/sbin",
        "/lib",
        "/usr",
        "/usr/bin",
        "/var",
        "/var/log",
        "/etc",
        "/tmp",
        "/run"
    };
    size_t path_count = sizeof(fhs_paths) / sizeof(fhs_paths[0]);
    fhs_entry_info_t info;

    printf("=== ЗВІТ ІНСПЕКЦІЇ ІЄРАРХІЇ FHS 3.0 (C Impl) ===\n\n");

    int usrmerge_active = 1;

    for (size_t i = 0; i < path_count; ++i) {
        if (inspect_fhs_path(fhs_paths[i], &info) == 0) {
            print_fhs_report(&info);
            if ((strcmp(fhs_paths[i], "/bin") == 0 || strcmp(fhs_paths[i], "/lib") == 0) && !info.is_symlink) {
                usrmerge_active = 0;
            }
        } else {
            printf("Каталог: %-12s | Стан: ВІДСУТНІЙ (%s)\n", fhs_paths[i], strerror(errno));
        }
    }

    printf("\nСтатус usrmerge: %s\n", usrmerge_active ? "АКТИВНО (успішно об'єднано)" : "ТРАДИЦІЙНИЙ (окремі каталоги)");

    return EXIT_SUCCESS;
}
